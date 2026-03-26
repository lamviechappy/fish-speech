# Long Script Generation with Block Mode

## Overview

For long scripts (e.g., audiobooks, long articles), generating all audio at once can cause:
- **Out of Memory (OOM)** errors
- **Overheating** on Mac
- **Long wait times** before getting any output

The **Block Mode** feature solves these issues by:
1. Splitting text into **sentence-aware chunks**
2. Processing chunks in **blocks** (e.g., 5 chunks per block)
3. Saving each block to a **temporary file**
4. Optionally **resting** between blocks (Love My Mac mode)
5. Concatenating all blocks into the final output

## Key Features

### Sentence-Aware Chunking

Chunks are defined by `chunk_length` (max characters) but **always end at complete sentence boundaries**:

```
❌ Bad: "Hello world. This is a te|st sentence."
✅ Good: "Hello world. This is a test sentence.|"
```

This ensures natural prosody and prevents broken sentences.

### Block Mode

After generating `z` chunks, the audio is saved to a temporary file:

```
Block 1: [chunk1, chunk2, chunk3, chunk4, chunk5] → temp_audio_blocks/block_0000.wav
Block 2: [chunk6, chunk7, chunk8, chunk9, chunk10] → temp_audio_blocks/block_0001.wav
...
Final: Concatenate all blocks → final_output.wav
```

### Love My Mac Mode

Between blocks, the system can rest for `x` seconds to prevent overheating:

```
Generate Block 1 → Save → Rest 10s → Generate Block 2 → Save → Rest 10s → ...
```

## API Usage

### List Available Presets

```
GET /v1/tts/presets
```

Returns a list of available presets with their configurations:

```bash
curl http://127.0.0.1:8080/v1/tts/presets
```

Response:
```json
{
  "success": true,
  "presets": [
    {
      "name": "short",
      "description": "For scripts 1000-5000 characters. No rest intervals, fast generation.",
      "chunk_length": 300,
      "block_size": 5,
      "rest_interval": 0.0
    },
    {
      "name": "medium",
      "description": "For scripts 5000-10000 characters. Light rest intervals.",
      "chunk_length": 250,
      "block_size": 5,
      "rest_interval": 3.0
    },
    {
      "name": "long",
      "description": "For scripts 10000-20000 characters. Moderate rest intervals.",
      "chunk_length": 250,
      "block_size": 5,
      "rest_interval": 5.0
    },
    {
      "name": "very-long",
      "description": "For scripts 20000+ characters (audiobooks). Conservative settings with longer rest.",
      "chunk_length": 200,
      "block_size": 3,
      "rest_interval": 10.0
    },
    {
      "name": "custom",
      "description": "Custom settings. Specify your own chunk_length, block_size, and rest_interval.",
      "chunk_length": 300,
      "block_size": 5,
      "rest_interval": 0.0
    }
  ],
  "message": "Found 5 presets"
}
```

### Endpoint

```
POST /v1/tts/long-script
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | required | Long text to generate |
| `reference_id` | string | optional | Saved reference voice ID |
| `references` | array | optional | Upload reference voices |
| `preset` | string | null | Preset name: "short", "medium", "long", "very-long", or "custom" |
| `chunk_length` | int | 300 | Max characters per chunk (respects sentence boundaries) |
| `block_size` | int | 5 | Number of chunks per block |
| `rest_interval` | float | 0.0 | Seconds to rest between blocks (Love My Mac mode) |
| `format` | string | "wav" | Output format (wav, mp3, flac) |
| `streaming` | bool | false | Keep temp files if true |

**Note**: If `preset` is specified (and not "custom"), it will override `chunk_length`, `block_size`, and `rest_interval`.

### Example: Using Presets (Recommended)

```bash
# Short script (1000-5000 chars)
curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here...",
    "reference_id": "my-voice",
    "preset": "short",
    "format": "wav"
  }' \
  --output output.wav

# Medium script (5000-10000 chars)
curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your longer text here...",
    "reference_id": "my-voice",
    "preset": "medium",
    "format": "wav"
  }' \
  --output output.wav

# Long script (10000-20000 chars)
curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your very long text here...",
    "reference_id": "my-voice",
    "preset": "long",
    "format": "wav"
  }' \
  --output output.wav

# Very long script / audiobook (20000+ chars)
curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your audiobook text here...",
    "reference_id": "narrator-voice",
    "preset": "very-long",
    "format": "wav"
  }' \
  --output audiobook.wav
```

### Example: Basic Long Script

```bash
curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Very long text here... (thousands of characters)",
    "reference_id": "my-voice",
    "preset": "medium",
    "format": "wav"
  }' \
  --output long_output.wav
```

### Example: Custom Settings (No Preset)

If you want full control over the parameters, use `preset: "custom"` or omit the preset field:

```bash
curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Very long text here...",
    "reference_id": "my-voice",
    "preset": "custom",
    "chunk_length": 250,
    "block_size": 4,
    "rest_interval": 7.0,
    "format": "wav"
  }' \
  --output long_output.wav
```

### Example: Love My Mac Mode (Rest Between Blocks)

```bash
curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Very long text here...",
    "reference_id": "my-voice",
    "preset": "long",
    "format": "wav"
  }' \
  --output long_output.wav
```

The "long" preset includes 5 seconds rest between blocks. For more rest, use "very-long" (10 seconds) or custom settings.

### Example: Multi-Speaker Long Dialogue

```bash
curl -X POST http://127.0.0.1:8080/v1/tts/long-script \
  -H "Content-Type: application/json" \
  -d '{
    "text": "<|speaker:0|>Long dialogue from speaker 0... <|speaker:1|>Long response from speaker 1...",
    "reference_id": "dialogue",
    "preset": "medium",
    "format": "wav"
  }' \
  --output dialogue_long.wav
```

## Python Example

```python
import requests

# Long script text
long_text = """
Chapter 1: The Beginning

Once upon a time, in a land far away, there lived a young programmer.
This programmer loved to write code and build amazing things.
One day, they discovered Fish Speech and decided to create an audiobook.

[Continue with thousands of characters...]
"""

# Option 1: Using a preset (recommended)
response = requests.post(
    "http://127.0.0.1:8080/v1/tts/long-script",
    json={
        "text": long_text,
        "reference_id": "narrator-voice",
        "preset": "long",  # Automatically configures optimal settings
        "format": "wav",
    },
)

# Save output
with open("audiobook.wav", "wb") as f:
    f.write(response.content)

print("Audiobook generated successfully!")

# Option 2: Custom settings
response = requests.post(
    "http://127.0.0.1:8080/v1/tts/long-script",
    json={
        "text": long_text,
        "reference_id": "narrator-voice",
        "preset": "custom",
        "chunk_length": 250,
        "block_size": 4,
        "rest_interval": 8.0,
        "format": "wav",
    },
)

with open("audiobook_custom.wav", "wb") as f:
    f.write(response.content)

# Option 3: List available presets first
presets_response = requests.get("http://127.0.0.1:8080/v1/tts/presets")
presets = presets_response.json()["presets"]

print("Available presets:")
for preset in presets:
    print(f"  - {preset['name']}: {preset['description']}")
```

## How It Works

### 1. Text Splitting

```python
from fish_speech.inference_engine.long_script_utils import split_into_sentence_chunks

text = "Hello world. This is a test. How are you?"
chunks = split_into_sentence_chunks(text, max_chunk_length=20)
# Result: ["Hello world.", "This is a test.", "How are you?"]
```

### 2. Block Processing

```
Input: 12 chunks, block_size=5

Block 0: chunks 0-4   → block_0000.wav
Block 1: chunks 5-9   → block_0001.wav
Block 2: chunks 10-11 → block_0002.wav

Final: Concatenate all blocks → final_output.wav
```

### 3. Memory Management

After each block:
- Audio is saved to disk
- Memory is freed
- Optional rest interval
- Next block starts fresh

## Recommended Settings

### Presets Overview

| Preset | Text Length | Chunk Length | Block Size | Rest Interval | Best For |
|--------|-------------|--------------|------------|---------------|----------|
| **short** | 1,000-5,000 chars | 300 | 5 | 0s | Articles, blog posts |
| **medium** | 5,000-10,000 chars | 250 | 5 | 3s | Long articles, short stories |
| **long** | 10,000-20,000 chars | 250 | 5 | 5s | Chapters, essays |
| **very-long** | 20,000+ chars | 200 | 3 | 10s | Audiobooks, novels |
| **custom** | Any | Custom | Custom | Custom | Full control |

### Quick Guide

**Just getting started?** Use presets:
- Short text → `"preset": "short"`
- Medium text → `"preset": "medium"`
- Long text → `"preset": "long"`
- Audiobook → `"preset": "very-long"`

**Need custom settings?** Use `"preset": "custom"` and specify your own values.

### For Short Scripts (< 1000 chars)

Use regular `/v1/tts` endpoint (no need for block mode).

### Using Presets (Recommended)

Simply specify the preset that matches your text length:

```json
{
  "text": "Your text here...",
  "reference_id": "my-voice",
  "preset": "medium"
}
```

The preset automatically configures optimal settings for that text length.

## Temporary Files

Temporary files are saved to `temp_audio_blocks/`:

```
temp_audio_blocks/
├── block_0000.wav
├── block_0001.wav
├── block_0002.wav
└── final_output.wav
```

By default, these are **automatically cleaned up** after generation.

To keep temporary files (for debugging), set `streaming: true`:

```json
{
  "text": "...",
  "streaming": true
}
```

## Performance

### Without Block Mode

- **Memory**: Grows linearly with text length
- **Risk**: OOM errors on long scripts
- **Wait time**: Must wait for entire generation

### With Block Mode

- **Memory**: Constant (only one block in memory)
- **Risk**: No OOM errors
- **Wait time**: Incremental progress (blocks saved as they complete)
- **Mac temperature**: Controlled with rest intervals

## Troubleshooting

### "Out of Memory" Error

Reduce `block_size` and `chunk_length`:

```json
{
  "chunk_length": 150,
  "block_size": 3,
  "rest_interval": 10.0
}
```

### Mac Overheating

Increase `rest_interval`:

```json
{
  "rest_interval": 15.0
}
```

### Broken Sentences

The system automatically respects sentence boundaries. If you still get broken sentences, check that your text has proper punctuation (`.`, `!`, `?`).

### Slow Generation

This is expected for very long scripts. Monitor progress in the server logs:

```
Generating chunk 1/50: Hello world...
Saved block 0 to temp_audio_blocks/block_0000.wav
Resting for 10.0s...
Generating chunk 6/50: This is a test...
```

## Comparison: Regular vs Block Mode

| Feature | Regular `/v1/tts` | Block Mode `/v1/tts/long-script` |
|---------|-------------------|----------------------------------|
| Max text length | ~2000 chars | Unlimited |
| Memory usage | High (grows with text) | Low (constant) |
| OOM risk | High for long scripts | None |
| Overheating risk | High for long scripts | Low (with rest intervals) |
| Incremental progress | No | Yes (blocks saved) |
| Best for | Short scripts | Long scripts, audiobooks |

## Next Steps

1. Test with a medium-length script (2000-5000 chars)
2. Monitor memory usage and temperature
3. Adjust `block_size` and `rest_interval` as needed
4. For production, consider adding progress callbacks

---

**Status**: ✅ Implemented in v0.2.0
**Date**: 2026-03-25
