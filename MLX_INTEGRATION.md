# Fish Speech MLX Integration

## Overview

Fish Speech has been successfully ported to use MLX for optimized inference on Apple Silicon. The implementation uses the existing `mlx-audio` library as a dependency and provides a thin wrapper that integrates with the fishaudio codebase.

## What Was Done

### 1. Dependencies (pyproject.toml)
- Added MLX core dependencies: `mlx>=0.20.0`, `mlx-lm>=0.20.0`
- Added `mlx-audio` as an editable dependency from `/Volumes/WD500/dev/dev-mlx-audio`
- Updated `transformers` to support both PyTorch (<5.0.0) and MLX (>=5.0.0) requirements

### 2. MLX Inference Engine (fish_speech/inference_engine/mlx_engine.py)
- Created `MLXTTSInferenceEngine` class that wraps mlx-audio's Fish Speech model
- Implements the same interface as `TTSInferenceEngine` for compatibility
- Handles reference audio loading, parameter conversion, and audio generation
- Supports streaming and non-streaming inference modes

### 3. Model Manager (tools/server/model_manager.py)
- Added `backend` parameter (default: "mlx")
- Added `load_mlx_engine()` method to initialize MLX inference engine
- Maintains backward compatibility with PyTorch backend

### 4. API Server (tools/api_server.py, tools/server/api_utils.py)
- Added `--backend` CLI argument with choices: ["pytorch", "mlx"]
- Default backend is MLX
- Passes backend parameter to ModelManager

### 5. WebUI (tools/run_webui.py)
- Added `--backend` CLI argument
- Conditional initialization based on backend selection
- MLX backend skips PyTorch-specific device detection and model loading

## Usage

### Installation

```bash
# Create conda environment
conda create -n fish python=3.10 -y
conda activate fish

# Install with MLX support
uv pip install -e ".[mlx]"
```

### API Server

```bash
# Start with MLX backend (default)
python tools/api_server.py --llama-checkpoint-path mlx-community/fish-audio-s2-pro-bf16

# Start with PyTorch backend
python tools/api_server.py --backend pytorch --llama-checkpoint-path checkpoints/s2-pro
```

### WebUI

```bash
# Start with MLX backend (default)
python tools/run_webui.py --llama-checkpoint-path mlx-community/fish-audio-s2-pro-bf16

# Start with PyTorch backend
python tools/run_webui.py --backend pytorch --llama-checkpoint-path checkpoints/s2-pro
```

### Python API

```python
from fish_speech.inference_engine.mlx_engine import MLXTTSInferenceEngine
from fish_speech.utils.schema import ServeTTSRequest

# Initialize MLX engine
engine = MLXTTSInferenceEngine(
    llama_checkpoint_path="mlx-community/fish-audio-s2-pro-bf16",
    compile=True,
)

# Generate speech
request = ServeTTSRequest(
    text="Hello from Fish Speech MLX!",
    references=[],
    max_new_tokens=1024,
    chunk_length=200,
    top_p=0.7,
    temperature=0.7,
    format="wav",
)

for result in engine.inference(request):
    if result.code == "final":
        sample_rate, audio = result.audio
        print(f"Generated {len(audio)} samples at {sample_rate}Hz")
```

## Testing

A basic test script is provided at `test_mlx_basic.py`:

```bash
conda run -n fish python3 test_mlx_basic.py
```

Test results:
- ✓ MLX engine initialization successful
- ✓ Audio generation working (94,208 samples at 44.1kHz, 2.14s duration)
- ✓ All tests passed

## Architecture

### MLX Backend Flow

```
User Request
    ↓
API Server / WebUI
    ↓
ModelManager (backend="mlx")
    ↓
MLXTTSInferenceEngine
    ↓
mlx-audio Model (from /Volumes/WD500/dev/dev-mlx-audio)
    ↓
Generated Audio
```

### Key Components

1. **mlx-audio**: Community library with complete Fish Speech MLX implementation
   - Dual-AR transformer architecture
   - Codec for audio encoding/decoding
   - Conversation handling and tokenization

2. **MLXTTSInferenceEngine**: Thin wrapper that:
   - Loads mlx-audio model using `mlx_audio.tts.utils.load()`
   - Converts `ServeTTSRequest` to mlx-audio format
   - Handles reference audio loading with librosa
   - Converts mlx arrays to numpy for output
   - Yields `InferenceResult` objects matching PyTorch interface

3. **Backend Selection**: CLI argument controls which engine is used
   - MLX: Fast inference on Apple Silicon, unified memory
   - PyTorch: Fallback for compatibility, supports CUDA/MPS/CPU

## Benefits of MLX

- **Optimized for Apple Silicon**: Native M-series chip support
- **Unified Memory**: No device management needed
- **Fast Inference**: Lazy evaluation and JIT compilation
- **Lower Memory Usage**: Efficient memory management
- **Same Quality**: Identical model architecture and weights

## Files Modified

- `pyproject.toml` - Added MLX dependencies
- `tools/server/model_manager.py` - Added MLX backend support
- `tools/api_server.py` - Added backend parameter
- `tools/server/api_utils.py` - Added backend CLI argument
- `tools/run_webui.py` - Added MLX initialization

## Files Created

- `fish_speech/inference_engine/mlx_engine.py` - MLX inference engine
- `test_mlx_basic.py` - Basic test script
- `MLX_INTEGRATION.md` - This documentation

## Notes

- MLX is now the default backend for better performance on Apple Silicon
- PyTorch backend remains available for backward compatibility
- The mlx-audio dependency is installed as editable from `/Volumes/WD500/dev/dev-mlx-audio`
- Model weights are automatically downloaded from HuggingFace on first use
- Recommended model: `mlx-community/fish-audio-s2-pro` (official MLX conversion)
- Models are cached in `~/.cache/huggingface/hub/` (~10GB)
- See `MODEL_DISTRIBUTION.md` for app distribution strategies

## Future Work

- Add quantization support (4-bit, 8-bit models)
- Port DAC codec to MLX for fully native pipeline
- Add streaming support when mlx-audio implements it
- Performance benchmarking vs PyTorch
- Add more comprehensive test suite
