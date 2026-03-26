#!/usr/bin/env python3
"""
Quick test for long script generation feature.
"""

from fish_speech.inference_engine.long_script_utils import split_into_sentence_chunks
from fish_speech.inference_engine.presets import list_presets, get_preset, apply_preset
from fish_speech.utils.schema import ServeLongScriptRequest


def test_sentence_chunking():
    """Test sentence-aware chunking."""
    print("Testing sentence-aware chunking...")

    text = "Hello world. This is a test. How are you? I am fine. Thank you for asking."
    chunks = split_into_sentence_chunks(text, max_chunk_length=30)

    print(f"Input: {text}")
    print(f"Chunks ({len(chunks)}):")
    for i, chunk in enumerate(chunks):
        print(f"  {i+1}. {chunk}")

    # Verify no broken sentences
    for chunk in chunks:
        assert chunk.strip().endswith(('.', '!', '?')), f"Broken sentence: {chunk}"

    print("✓ Sentence chunking works correctly\n")


def test_presets():
    """Test preset system."""
    print("Testing preset system...")

    presets = list_presets()
    print(f"Found {len(presets)} presets:")
    for preset in presets:
        print(f"  - {preset.name}: {preset.description}")

    # Test getting specific preset
    long_preset = get_preset("long")
    print(f"\n'long' preset settings:")
    print(f"  chunk_length: {long_preset.chunk_length}")
    print(f"  block_size: {long_preset.block_size}")
    print(f"  rest_interval: {long_preset.rest_interval}")

    print("✓ Preset system works correctly\n")


def test_apply_preset():
    """Test applying preset to request."""
    print("Testing preset application...")

    request = ServeLongScriptRequest(
        text="Test text",
        preset="medium",
        chunk_length=500,  # Should be overridden
        block_size=10,    # Should be overridden
        rest_interval=20.0,  # Should be overridden
    )

    print(f"Before applying preset:")
    print(f"  chunk_length: {request.chunk_length}")
    print(f"  block_size: {request.block_size}")
    print(f"  rest_interval: {request.rest_interval}")

    request = apply_preset(request, "medium")

    print(f"\nAfter applying 'medium' preset:")
    print(f"  chunk_length: {request.chunk_length}")
    print(f"  block_size: {request.block_size}")
    print(f"  rest_interval: {request.rest_interval}")

    # Verify preset was applied
    medium_preset = get_preset("medium")
    assert request.chunk_length == medium_preset.chunk_length
    assert request.block_size == medium_preset.block_size
    assert request.rest_interval == medium_preset.rest_interval

    print("✓ Preset application works correctly\n")


def test_custom_preset():
    """Test custom preset (should not override)."""
    print("Testing custom preset...")

    request = ServeLongScriptRequest(
        text="Test text",
        preset="custom",
        chunk_length=123,
        block_size=7,
        rest_interval=15.0,
    )

    print(f"Custom settings:")
    print(f"  chunk_length: {request.chunk_length}")
    print(f"  block_size: {request.block_size}")
    print(f"  rest_interval: {request.rest_interval}")

    request = apply_preset(request, "custom")

    print(f"\nAfter applying 'custom' preset (should not change):")
    print(f"  chunk_length: {request.chunk_length}")
    print(f"  block_size: {request.block_size}")
    print(f"  rest_interval: {request.rest_interval}")

    # Verify custom values were preserved
    assert request.chunk_length == 123
    assert request.block_size == 7
    assert request.rest_interval == 15.0

    print("✓ Custom preset works correctly\n")


if __name__ == "__main__":
    print("=" * 80)
    print("LONG SCRIPT GENERATION FEATURE - UNIT TESTS")
    print("=" * 80)
    print()

    try:
        test_sentence_chunking()
        test_presets()
        test_apply_preset()
        test_custom_preset()

        print("=" * 80)
        print("ALL TESTS PASSED ✓")
        print("=" * 80)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
