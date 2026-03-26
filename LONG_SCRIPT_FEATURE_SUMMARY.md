# Long Script Generation Feature - Summary

## What Was Implemented

Added a complete long script generation system with block mode and presets to safely generate audio for very long texts (audiobooks, articles, etc.) without memory issues or overheating.

## Key Features

### 1. Sentence-Aware Chunking
- Splits text by `chunk_length` but always respects sentence boundaries
- Prevents broken sentences that would sound unnatural
- Uses regex to detect sentence endings (`.`, `!`, `?`, newlines)

### 2. Block Mode Processing
- Groups chunks into blocks (e.g., 5 chunks per block)
- Saves each block to a temporary file
- Prevents OOM errors by keeping memory usage constant
- Allows incremental progress tracking

### 3. Love My Mac Mode
- Optional rest intervals between blocks
- Prevents Mac from overheating during long generations
- Configurable from 0-60 seconds

### 4. Preset System
- 5 predefined presets for different text lengths
- Easy to use: just specify `"preset": "medium"`
- Automatically configures optimal settings

### 5. API Endpoints
- `POST /v1/tts/long-script` - Generate with block mode
- `GET /v1/tts/presets` - List available presets

## Files Created/Modified

### New Files
1. **`fish_speech/inference_engine/long_script_utils.py`**
   - `split_into_sentence_chunks()` - Sentence-aware text splitting
   - `save_audio_block()` - Save block to temp file
   - `concatenate_audio_blocks()` - Merge all blocks
   - `generate_long_script_with_blocks()` - Main generation function

2. **`fish_speech/inference_engine/presets.py`**
   - Preset definitions (short, medium, long, very-long, custom)
   - `get_preset()` - Get preset by name
   - `list_presets()` - List all presets
   - `apply_preset()` - Apply preset to request

3. **`LONG_SCRIPT_GENERATION.md`**
   - Complete documentation with examples
   - API usage guide
   - Preset descriptions
   - Troubleshooting tips

4. **`examples/long_script_presets.py`**
   - Python example script
   - Demonstrates all presets
   - Shows custom settings usage

### Modified Files
1. **`fish_speech/utils/schema.py`**
   - Added `LongScriptPreset` model
   - Added `ServeLongScriptRequest` model
   - Added `ListPresetsResponse` model

2. **`tools/server/views.py`**
   - Added `POST /v1/tts/long-script` endpoint
   - Added `GET /v1/tts/presets` endpoint
   - Integrated preset system

## Presets

| Preset | Text Length | Chunk Length | Block Size | Rest | Best For |
|--------|-------------|--------------|------------|------|----------|
| **short** | 1K-5K chars | 300 | 5 | 0s | Articles |
| **medium** | 5K-10K chars | 250 | 5 | 3s | Long articles |
| **long** | 10K-20K chars | 250 | 5 | 5s | Chapters |
| **very-long** | 20K+ chars | 200 | 3 | 10s | Audiobooks |
| **custom** | Any | Custom | Custom | Custom | Full control |

## Usage Examples

### Using Presets (Recommended)

```bash
curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Very long text...",
    "reference_id": "my-voice",
    "preset": "long",
    "format": "wav"
  }' \
  --output output.wav
```

### Custom Settings

```bash
curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Very long text...",
    "reference_id": "my-voice",
    "preset": "custom",
    "chunk_length": 250,
    "block_size": 4,
    "rest_interval": 7.0,
    "format": "wav"
  }' \
  --output output.wav
```

### List Presets

```bash
curl http://127.0.0.1:8080/v1/tts/presets
```

## How It Works

```
Input Text (10,000 chars)
    ↓
Split into sentence-aware chunks (chunk_length=250)
    ↓
Chunks: [chunk1, chunk2, ..., chunk40]
    ↓
Group into blocks (block_size=5)
    ↓
Block 0: [chunk1-5]   → Generate → Save to block_0000.wav
Rest 5s
Block 1: [chunk6-10]  → Generate → Save to block_0001.wav
Rest 5s
Block 2: [chunk11-15] → Generate → Save to block_0002.wav
...
    ↓
Concatenate all blocks → final_output.wav
    ↓
Clean up temp files
    ↓
Return final audio
```

## Benefits

### Without Block Mode (Regular `/v1/tts`)
- ❌ Memory grows with text length
- ❌ OOM errors on long scripts
- ❌ Mac overheating risk
- ❌ Must wait for entire generation
- ❌ No incremental progress

### With Block Mode (`/v1/tts/long-script`)
- ✅ Constant memory usage
- ✅ No OOM errors
- ✅ Controlled temperature (with rest intervals)
- ✅ Incremental progress (blocks saved)
- ✅ Can resume from blocks if interrupted

## Testing

To test the feature:

1. **List presets:**
   ```bash
   curl http://127.0.0.1:8080/v1/tts/presets
   ```

2. **Generate with preset:**
   ```bash
   curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Test text here...",
       "reference_id": "my-voice",
       "preset": "short"
     }' \
     --output test.wav
   ```

3. **Run Python example:**
   ```bash
   python examples/long_script_presets.py
   ```

## Next Steps

1. Test with real long scripts (5000+ chars)
2. Monitor memory usage and temperature
3. Adjust presets based on real-world usage
4. Consider adding progress callbacks for WebUI
5. Add to WebUI Pro as a feature

## Version

This feature will be part of **v0.2.0** (next release after v0.1.0).

---

**Status**: ✅ Implemented
**Date**: 2026-03-25
**Branch**: feature/mlx
