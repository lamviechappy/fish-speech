# Testing Multi-Speaker Reference Voices

## How to Test

### 1. Create a multi-speaker reference directory

```bash
mkdir -p references/dialogue
```

### 2. Add two speaker audio files

You need TWO audio files with their corresponding text:

```
references/dialogue/
├── speaker0.wav  (or .mp3, .flac)
├── speaker0.lab  (text for speaker 0)
├── speaker1.wav
└── speaker1.lab  (text for speaker 1)
```

### 3. Test with dialogue text

```bash
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "<|speaker:0|>[excited] Hello! <|speaker:1|>[calm] Hi there.",
    "reference_id": "dialogue",
    "format": "wav"
  }' \
  --output dialogue_test.wav
```

## How It Works Now

The updated MLX engine:

1. **Loads ALL audio files** from the reference directory (not just one)
2. **Encodes each reference** separately using the codec
3. **Builds a conversation** with proper speaker tags (`<|speaker:0|>`, `<|speaker:1|>`)
4. **Generates audio** that matches each speaker's voice

## Key Changes

### Before (Wrong)
- Only loaded the first audio file
- Single reference for all speakers
- Dialogue mode didn't work properly

### After (Correct)
- Loads ALL audio files from reference directory
- Multiple references for multiple speakers
- mlx-audio automatically tags them as `<|speaker:0|>`, `<|speaker:1|>`, etc.
- Dialogue mode works correctly

## Example Reference Structure

### Single Speaker
```
references/john/
├── sample.wav
└── sample.lab
```

### Multi-Speaker Dialogue
```
references/conversation/
├── alice.wav
├── alice.lab
├── bob.wav
└── bob.lab
```

When you use `reference_id: "conversation"`, both Alice and Bob's voices will be loaded, and you can use:
```
<|speaker:0|>This is Alice speaking.
<|speaker:1|>And this is Bob.
```

## Testing Checklist

- [ ] Single speaker reference works
- [ ] Multi-speaker reference loads all files
- [ ] Dialogue with `<|speaker:0|>` and `<|speaker:1|>` uses correct voices
- [ ] Emotion tags work with references
- [ ] Generation without references still works

## Notes

- Files are loaded in **sorted order** (alphabetically)
- First file = `<|speaker:0|>`, second file = `<|speaker:1|>`, etc.
- You can have up to 5 speakers (mlx-audio default)
- Both `.lab` and `.txt` files are supported for text
