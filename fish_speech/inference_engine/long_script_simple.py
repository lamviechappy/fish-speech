"""
Simplified long script generation - just split and call regular TTS multiple times.
"""

import io
import time
from pathlib import Path
from typing import List, Tuple
import numpy as np


def generate_long_script_simple(
    engine,
    text: str,
    chunk_length: int = 300,
    rest_interval: float = 0.0,
    **kwargs
) -> Tuple[np.ndarray, int]:
    """
    Simplified long script generation.

    Just splits text and calls regular TTS for each chunk.
    No block mode, just simple concatenation.
    """
    from loguru import logger
    from fish_speech.inference_engine.long_script_utils import split_into_sentence_chunks
    from fish_speech.utils.schema import ServeTTSRequest

    logger.info(f"[SIMPLE] Starting simple long script generation")
    logger.info(f"[SIMPLE] Text length: {len(text)}, chunk_length: {chunk_length}")

    # Split text
    chunks = split_into_sentence_chunks(text, max_chunk_length=chunk_length)
    logger.info(f"[SIMPLE] Split into {len(chunks)} chunks")

    all_audio = []
    sample_rate = None

    for i, chunk_text in enumerate(chunks):
        logger.info(f"[SIMPLE] Processing chunk {i+1}/{len(chunks)}: {chunk_text[:50]}...")

        # Create request
        chunk_request = ServeTTSRequest(
            text=chunk_text,
            chunk_length=chunk_length,
            format="wav",
            streaming=False,
            **kwargs
        )

        # Generate - properly consume the generator
        logger.info(f"[SIMPLE] Calling engine.inference()")
        chunk_audio = None

        try:
            for result in engine.inference(chunk_request):
                logger.info(f"[SIMPLE] Got result: {result.code}")

                if result.code == "final":
                    if isinstance(result.audio, tuple):
                        sr, audio_np = result.audio
                        sample_rate = sr
                        chunk_audio = audio_np
                        logger.info(f"[SIMPLE] Got audio, shape: {audio_np.shape}")
                    break

                elif result.code == "error":
                    logger.error(f"[SIMPLE] Error: {result.error}")
                    raise result.error

        except Exception as e:
            logger.error(f"[SIMPLE] Exception during generation: {e}")
            raise

        if chunk_audio is None:
            raise RuntimeError(f"Failed to generate chunk {i}")

        all_audio.append(chunk_audio)
        logger.info(f"[SIMPLE] Chunk {i+1} done")

        # Rest if needed
        if rest_interval > 0 and i < len(chunks) - 1:
            logger.info(f"[SIMPLE] Resting {rest_interval}s...")
            time.sleep(rest_interval)

    # Concatenate
    logger.info(f"[SIMPLE] Concatenating {len(all_audio)} chunks")
    final_audio = np.concatenate(all_audio, axis=0)
    logger.info(f"[SIMPLE] Final audio shape: {final_audio.shape}")

    return final_audio, sample_rate
