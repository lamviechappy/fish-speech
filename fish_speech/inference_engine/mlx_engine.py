"""
MLX-based inference engine for Fish Speech.

This module provides an MLX implementation of the TTS inference engine,
wrapping the mlx-audio Fish Speech model to match the fishaudio interface.
"""

import gc
import re
import shutil
from pathlib import Path
from typing import Generator, Optional

import mlx.core as mx
import numpy as np

from fish_speech.inference_engine.utils import InferenceResult
from fish_speech.utils.schema import ServeTTSRequest

try:
    from mlx_audio.tts.utils import load as load_mlx_model
except ImportError:
    raise ImportError(
        "mlx-audio is required for MLX inference. "
        "Install it with: uv pip install -e /Volumes/WD500/dev/dev-mlx-audio"
    )

_ID_PATTERN = re.compile(r"^[a-zA-Z0-9\-_ ]+$")


class MLXTTSInferenceEngine:
    """
    MLX-based TTS inference engine that wraps mlx-audio's Fish Speech implementation.

    This engine adapts the mlx-audio Model to match the fishaudio TTSInferenceEngine
    interface, allowing seamless integration with the existing API server and WebUI.
    """

    def __init__(
        self,
        llama_checkpoint_path: str,
        device: str = "mps",
        compile: bool = True,
        precision: str = "float16",
        **kwargs,
    ):
        """
        Initialize the MLX inference engine.

        Args:
            llama_checkpoint_path: Path to the model checkpoint or HuggingFace model ID
            device: Device to use (ignored for MLX, uses unified memory)
            compile: Whether to use MLX compilation (default: True)
            precision: Model precision (default: float16)
            **kwargs: Additional arguments (ignored, for compatibility)
        """
        self.llama_checkpoint_path = llama_checkpoint_path
        self.compile = compile
        self.precision = precision

        # Load the MLX model using mlx-audio's load function
        self.model = load_mlx_model(llama_checkpoint_path)

        # Get sample rate from model config
        self.sample_rate = getattr(
            self.model.config.audio_decoder_config, "sampling_rate", 44100
        )

        # Create a mock decoder_model object for compatibility with API server
        # The API server expects engine.decoder_model.sample_rate
        class MockDecoder:
            def __init__(self, sample_rate):
                self.sample_rate = sample_rate

        self.decoder_model = MockDecoder(self.sample_rate)

        # Initialize reference cache (for compatibility with API server)
        self.ref_by_id = {}
        self.ref_by_hash = {}

    @staticmethod
    def _validate_id(id: str) -> None:
        """Validate reference ID format."""
        if not _ID_PATTERN.match(id) or len(id) > 255:
            raise ValueError(
                "Reference ID contains invalid characters or is too long. "
                "Only alphanumeric, hyphens, underscores, and spaces are allowed."
            )

    def add_reference(self, id: str, wav_file_path: str, reference_text: str) -> None:
        """
        Add a new reference voice by creating a new directory and copying files.

        Args:
            id: Reference ID (directory name)
            wav_file_path: Path to the audio file to copy
            reference_text: Text content for the .lab file

        Raises:
            FileExistsError: If the reference ID already exists
            FileNotFoundError: If the audio file doesn't exist
            OSError: If file operations fail
        """
        self._validate_id(id)

        # Check if reference already exists
        ref_dir = Path("references") / id
        if ref_dir.exists():
            raise FileExistsError(f"Reference ID '{id}' already exists")

        # Check if source audio file exists
        wav_path = Path(wav_file_path)
        if not wav_path.exists():
            raise FileNotFoundError(f"Audio file not found: {wav_file_path}")

        try:
            # Create reference directory
            ref_dir.mkdir(parents=True, exist_ok=True)

            # Copy audio file
            dest_audio = ref_dir / "reference.wav"
            shutil.copy2(wav_path, dest_audio)

            # Write reference text to .lab file (standard format)
            lab_file = ref_dir / "reference.lab"
            lab_file.write_text(reference_text, encoding="utf-8")

            # Clear cache for this ID if it exists
            if id in self.ref_by_id:
                del self.ref_by_id[id]

        except Exception as e:
            # Clean up on failure
            if ref_dir.exists():
                shutil.rmtree(ref_dir)
            raise OSError(f"Failed to add reference: {e}") from e

    def delete_reference(self, id: str) -> None:
        """
        Delete a reference voice by removing its directory and files.

        Args:
            id: Reference ID (directory name) to delete

        Raises:
            FileNotFoundError: If the reference ID doesn't exist
            OSError: If file operations fail
        """
        self._validate_id(id)

        ref_dir = Path("references") / id
        if not ref_dir.exists():
            raise FileNotFoundError(f"Reference ID '{id}' does not exist")

        try:
            # Remove the entire reference directory
            shutil.rmtree(ref_dir)

            # Clear cache for this ID
            if id in self.ref_by_id:
                del self.ref_by_id[id]

        except Exception as e:
            raise OSError(f"Failed to delete reference: {e}") from e

    def inference(self, req: ServeTTSRequest) -> Generator[InferenceResult, None, None]:
        """
        Perform TTS inference using the MLX model.

        Args:
            req: TTS request containing text, references, and generation parameters

        Yields:
            InferenceResult objects containing audio segments or errors
        """
        try:
            # Load reference audio if provided
            ref_audios = []
            ref_texts = []

            if req.references:
                # Load all references from the request
                import io
                import librosa
                import soundfile as sf

                for reference in req.references:
                    # reference.audio is bytes, need to convert to audio array
                    audio_bytes = io.BytesIO(reference.audio)
                    audio_np, sr = sf.read(audio_bytes)

                    # Resample if needed
                    if sr != self.sample_rate:
                        audio_np = librosa.resample(audio_np, orig_sr=sr, target_sr=self.sample_rate)

                    # Convert to mono if stereo
                    if audio_np.ndim == 2:
                        audio_np = audio_np.mean(axis=1)

                    ref_audios.append(audio_np)
                    ref_texts.append(reference.text)

            elif req.reference_id:
                # Load ALL reference files by ID from references/ directory
                import librosa
                from fish_speech.utils.file import AUDIO_EXTENSIONS

                ref_dir = Path("references") / req.reference_id
                if ref_dir.exists():
                    # Find ALL audio files in reference directory
                    audio_files = []
                    for ext in AUDIO_EXTENSIONS:
                        audio_files.extend(ref_dir.glob(f"*{ext}"))

                    # Sort for consistent ordering
                    audio_files = sorted(audio_files)

                    for audio_file in audio_files:
                        # Load audio
                        audio_np, sr = librosa.load(str(audio_file), sr=self.sample_rate, mono=True)
                        ref_audios.append(audio_np)

                        # Load reference text from .lab or .txt file
                        lab_file = audio_file.with_suffix(".lab")
                        txt_file = audio_file.with_suffix(".txt")

                        if lab_file.exists():
                            ref_texts.append(lab_file.read_text(encoding="utf-8").strip())
                        elif txt_file.exists():
                            ref_texts.append(txt_file.read_text(encoding="utf-8").strip())
                        else:
                            ref_texts.append("")  # Empty text if no label file

            # Convert to mlx-audio format
            # mlx-audio expects a single concatenated ref_audio and newline-separated ref_text
            # OR it can handle the conversation building internally
            if ref_audios and ref_texts:
                # For multi-speaker, we need to pass them to mlx-audio's generate method
                # which will build the conversation with proper speaker tags
                # mlx-audio's generate doesn't directly support multiple refs,
                # so we need to use the model's _build_conversation method

                # Encode all reference audios
                ref_tokens = []
                for audio_np in ref_audios:
                    audio_mx = mx.array(audio_np)
                    # Encode using the codec
                    if audio_mx.ndim == 1:
                        audio_mx = audio_mx[None, None, :]
                    elif audio_mx.ndim == 2:
                        audio_mx = audio_mx[None, :, :]
                    if audio_mx.shape[1] != 1:
                        audio_mx = mx.mean(audio_mx, axis=1, keepdims=True)

                    indices, feature_lengths = self.model.codec.encode(audio_mx)
                    prompt_length = int(feature_lengths[0].item())
                    ref_tokens.append(indices[0, :, :prompt_length])

                # Build conversation with multiple references
                base_conversation = self.model._build_conversation(ref_texts, ref_tokens)
            else:
                # No references
                base_conversation = self.model._build_conversation([], [])

            # Convert request parameters to mlx-audio format
            max_tokens = req.max_new_tokens if req.max_new_tokens else 1024
            temperature = req.temperature if req.temperature is not None else 0.7
            top_p = req.top_p if req.top_p is not None else 0.7
            top_k = 30  # mlx-audio default
            chunk_length = req.chunk_length if req.chunk_length else 300

            # Split text by speaker tags for batch processing
            from mlx_audio.tts.models.fish_qwen3_omni.prompt import (
                split_text_by_speaker,
                group_turns_into_batches,
            )

            turns = split_text_by_speaker(req.text)
            batches = (
                group_turns_into_batches(turns, max_speakers=5, max_bytes=chunk_length)
                if turns
                else [req.text]
            )

            # Generate audio for each batch
            from mlx_audio.tts.models.fish_qwen3_omni.prompt import Conversation, Message, TextPart, VQPart
            import time

            conversation = Conversation(list(base_conversation.messages))
            segments = []
            segment_idx = 0

            for batch_text in batches:
                conversation.append(
                    Message(
                        role="user",
                        parts=[TextPart(batch_text)],
                        add_im_start=True,
                        add_im_end=True,
                    )
                )

                start_time = time.perf_counter()
                codes = self.model._generate_codes_for_batch(
                    conversation=conversation,
                    batch_text=batch_text,
                    max_new_tokens=max_tokens,
                    top_p=top_p,
                    top_k=top_k,
                    temperature=temperature,
                )
                audio = self.model._decode_codes(codes)
                mx.eval(audio, codes)

                conversation.append(
                    Message(
                        role="assistant",
                        parts=[VQPart(codes)],
                        modality="voice",
                        add_im_start=True,
                        add_im_end=True,
                    )
                )

                # Convert mx.array to numpy
                audio_np = np.array(audio)

                if req.streaming:
                    # Yield intermediate segments for streaming
                    yield InferenceResult(
                        code="segment",
                        audio=(self.sample_rate, audio_np),
                        error=None,
                    )

                segments.append(audio_np)
                segment_idx += 1

            # Clean up memory
            gc.collect()

            # Check if any audio was generated
            if len(segments) == 0:
                yield InferenceResult(
                    code="error",
                    audio=None,
                    error=RuntimeError("No audio generated, please check the input text."),
                )
            else:
                # Return final concatenated audio
                audio = np.concatenate(segments, axis=0)
                yield InferenceResult(
                    code="final",
                    audio=(self.sample_rate, audio),
                    error=None,
                )

        except Exception as e:
            # Handle any errors during generation
            yield InferenceResult(
                code="error",
                audio=None,
                error=e,
            )

    def get_reference_audio_path(self, reference) -> Optional[str]:
        """
        Get the file path for a reference audio.

        Args:
            reference: Reference object containing audio information

        Returns:
            Path to the reference audio file, or None if not found
        """
        # Handle different reference formats
        if hasattr(reference, 'audio'):
            return reference.audio
        elif hasattr(reference, 'path'):
            return reference.path
        elif isinstance(reference, str):
            return reference
        return None
