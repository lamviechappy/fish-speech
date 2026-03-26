"""
Utilities for long script generation with block mode and sentence-aware chunking.

This module provides functions to safely generate long scripts by:
1. Splitting text into chunks that respect sentence boundaries
2. Processing chunks in blocks with optional rest intervals
3. Saving intermediate results to prevent data loss
"""

import re
import time
from pathlib import Path
from typing import List, Tuple
import numpy as np


def split_into_sentence_chunks(text: str, max_chunk_length: int = 300) -> List[str]:
    """
    Split text into chunks that respect sentence boundaries.

    Each chunk will be at most max_chunk_length characters, but will always
    end at a complete sentence boundary (., !, ?, or newline).

    Args:
        text: Input text to split
        max_chunk_length: Maximum characters per chunk (default: 300)

    Returns:
        List of text chunks, each ending at a sentence boundary
    """
    # Sentence boundary patterns
    sentence_end_pattern = re.compile(r'([.!?\n])\s+')

    chunks = []
    current_chunk = ""

    # Split by sentences
    sentences = sentence_end_pattern.split(text)

    # Reconstruct sentences with their punctuation
    reconstructed_sentences = []
    i = 0
    while i < len(sentences):
        if i + 1 < len(sentences) and sentences[i + 1] in '.!?\n':
            # Sentence with punctuation
            reconstructed_sentences.append(sentences[i] + sentences[i + 1])
            i += 2
        else:
            # Last sentence or sentence without punctuation
            if sentences[i].strip():
                reconstructed_sentences.append(sentences[i])
            i += 1

    # Group sentences into chunks
    for sentence in reconstructed_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # If adding this sentence would exceed max_chunk_length
        if current_chunk and len(current_chunk) + len(sentence) + 1 > max_chunk_length:
            # Save current chunk and start new one
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            # Add to current chunk
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence

    # Add remaining chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def save_audio_block(
    audio_segments: List[np.ndarray],
    sample_rate: int,
    output_dir: Path,
    block_index: int,
) -> Path:
    """
    Save a block of audio segments to a temporary file.

    Args:
        audio_segments: List of audio arrays to concatenate
        sample_rate: Audio sample rate
        output_dir: Directory to save temporary files
        block_index: Index of this block

    Returns:
        Path to the saved audio file
    """
    import soundfile as sf

    # Concatenate all segments in this block
    audio = np.concatenate(audio_segments, axis=0)

    # Create output directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save to temporary file
    output_path = output_dir / f"block_{block_index:04d}.wav"
    sf.write(output_path, audio, sample_rate)

    return output_path


def concatenate_audio_blocks(
    block_files: List[Path],
    output_path: Path,
    sample_rate: int,
) -> Path:
    """
    Concatenate all audio blocks into final output file.

    Args:
        block_files: List of temporary block files
        output_path: Final output file path
        sample_rate: Audio sample rate

    Returns:
        Path to the final output file
    """
    import soundfile as sf

    all_audio = []
    for block_file in block_files:
        audio, sr = sf.read(block_file)
        if sr != sample_rate:
            raise ValueError(f"Sample rate mismatch: {sr} != {sample_rate}")
        all_audio.append(audio)

    # Concatenate and save
    final_audio = np.concatenate(all_audio, axis=0)
    sf.write(output_path, final_audio, sample_rate)

    return output_path


def generate_long_script_with_blocks(
    engine,
    request,
    block_size: int = 5,
    rest_interval: float = 0.0,
    temp_dir: Path = Path("temp_audio_blocks"),
) -> Tuple[Path, List[Path]]:
    """
    Generate audio for long script using block mode.

    This function:
    1. Splits text into sentence-aware chunks
    2. Generates audio for chunks in blocks
    3. Saves each block to a temp file
    4. Optionally rests between blocks (Love My Mac mode)
    5. Returns paths to all block files

    Args:
        engine: TTS inference engine
        request: TTS request object
        block_size: Number of chunks per block (default: 5)
        rest_interval: Seconds to rest between blocks (default: 0.0)
        temp_dir: Directory for temporary block files

    Returns:
        Tuple of (final_output_path, list_of_block_files)
    """
    from loguru import logger
    from fish_speech.inference_engine.utils import InferenceResult

    logger.info(f"[LONG_SCRIPT] Starting generation for text length: {len(request.text)}")

    # Split text into sentence-aware chunks
    chunk_length = request.chunk_length if request.chunk_length else 300
    logger.info(f"[LONG_SCRIPT] Splitting text with chunk_length={chunk_length}")
    chunks = split_into_sentence_chunks(request.text, max_chunk_length=chunk_length)

    logger.info(f"[LONG_SCRIPT] Split text into {len(chunks)} chunks")
    logger.info(f"[LONG_SCRIPT] Processing in blocks of {block_size} chunks")
    if rest_interval > 0:
        logger.info(f"[LONG_SCRIPT] Resting {rest_interval}s between blocks (Love My Mac mode)")

    # Create temp directory
    logger.info(f"[LONG_SCRIPT] Creating temp directory: {temp_dir}")
    temp_dir.mkdir(parents=True, exist_ok=True)

    block_files = []
    current_block_segments = []
    block_index = 0

    # Process each chunk
    for chunk_idx, chunk_text in enumerate(chunks):
        logger.info(f"[LONG_SCRIPT] Generating chunk {chunk_idx + 1}/{len(chunks)}: {chunk_text[:50]}...")

        # Create a new request for this chunk
        from fish_speech.utils.schema import ServeTTSRequest
        logger.info(f"[LONG_SCRIPT] Creating ServeTTSRequest for chunk {chunk_idx + 1}")
        chunk_request = ServeTTSRequest(
            text=chunk_text,
            references=getattr(request, 'references', []),
            reference_id=getattr(request, 'reference_id', None),
            max_new_tokens=getattr(request, 'max_new_tokens', 1024),
            chunk_length=chunk_length,
            top_p=getattr(request, 'top_p', 0.8),
            temperature=getattr(request, 'temperature', 0.8),
            format=getattr(request, 'format', 'wav'),
            streaming=False,  # Don't stream individual chunks
        )

        # Generate audio for this chunk
        logger.info(f"[LONG_SCRIPT] Calling engine.inference() for chunk {chunk_idx + 1}")
        chunk_audio = None
        for result in engine.inference(chunk_request):
            logger.info(f"[LONG_SCRIPT] Got result code: {result.code}")
            if result.code == "final":
                sample_rate, audio_np = result.audio
                chunk_audio = audio_np
                logger.info(f"[LONG_SCRIPT] Chunk {chunk_idx + 1} generated successfully, audio shape: {audio_np.shape}")
                break
            elif result.code == "error":
                logger.error(f"[LONG_SCRIPT] Error generating chunk {chunk_idx + 1}: {result.error}")
                raise result.error

        if chunk_audio is None:
            logger.error(f"[LONG_SCRIPT] Failed to generate audio for chunk {chunk_idx}")
            raise RuntimeError(f"Failed to generate audio for chunk {chunk_idx}")

        current_block_segments.append(chunk_audio)
        logger.info(f"[LONG_SCRIPT] Added chunk {chunk_idx + 1} to current block")

        # Check if we've completed a block
        if len(current_block_segments) >= block_size or chunk_idx == len(chunks) - 1:
            logger.info(f"[LONG_SCRIPT] Saving block {block_index} with {len(current_block_segments)} segments")
            # Save this block
            block_file = save_audio_block(
                current_block_segments,
                sample_rate,
                temp_dir,
                block_index,
            )
            block_files.append(block_file)
            logger.info(f"[LONG_SCRIPT] Saved block {block_index} to {block_file}")

            # Reset for next block
            current_block_segments = []
            block_index += 1

            # Rest between blocks (Love My Mac mode)
            if rest_interval > 0 and chunk_idx < len(chunks) - 1:
                logger.info(f"[LONG_SCRIPT] Resting for {rest_interval}s...")
                time.sleep(rest_interval)

    # Concatenate all blocks into final output
    logger.info(f"[LONG_SCRIPT] Concatenating {len(block_files)} blocks")
    final_output = temp_dir / "final_output.wav"
    concatenate_audio_blocks(block_files, final_output, sample_rate)
    logger.info(f"[LONG_SCRIPT] Final output saved to {final_output}")

    return final_output, block_files
