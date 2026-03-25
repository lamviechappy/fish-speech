#!/usr/bin/env python3
"""Basic test script for MLX inference engine."""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from fish_speech.inference_engine.mlx_engine import MLXTTSInferenceEngine
from fish_speech.utils.schema import ServeTTSRequest

def test_mlx_engine_initialization():
    """Test that the MLX engine can be initialized."""
    print("Testing MLX engine initialization...")

    try:
        # Use a HuggingFace model ID for testing
        engine = MLXTTSInferenceEngine(
            llama_checkpoint_path="mlx-community/fish-audio-s2-pro",
            compile=True,
        )
        print("✓ MLX engine initialized successfully")
        return engine
    except Exception as e:
        print(f"✗ Failed to initialize MLX engine: {e}")
        raise

def test_mlx_inference(engine):
    """Test basic inference with the MLX engine."""
    print("\nTesting MLX inference...")

    try:
        request = ServeTTSRequest(
            text="Hello from Fish Speech MLX!",
            references=[],
            reference_id=None,
            max_new_tokens=512,
            chunk_length=200,
            top_p=0.7,
            repetition_penalty=1.2,
            temperature=0.7,
            format="wav",
        )

        results = list(engine.inference(request))

        if results:
            final_result = results[-1]
            if final_result.code == "final" and final_result.audio is not None:
                sample_rate, audio = final_result.audio
                print(f"✓ Generated audio: {len(audio)} samples at {sample_rate}Hz")
                print(f"  Duration: {len(audio) / sample_rate:.2f}s")
                return True
            else:
                print(f"✗ Unexpected result: {final_result.code}")
                return False
        else:
            print("✗ No results generated")
            return False

    except Exception as e:
        print(f"✗ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Fish Speech MLX Integration Test")
    print("=" * 60)

    try:
        engine = test_mlx_engine_initialization()
        success = test_mlx_inference(engine)

        print("\n" + "=" * 60)
        if success:
            print("✓ All tests passed!")
            sys.exit(0)
        else:
            print("✗ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Test suite failed: {e}")
        sys.exit(1)
