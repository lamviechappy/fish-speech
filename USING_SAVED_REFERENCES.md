# Using Saved Reference Voices

## List All Saved References

```bash
curl http://127.0.0.1:8080/v1/references/list
```

Response:
```json
{
  "success": true,
  "reference_ids": ["my-voice", "dialogue", "emily", "john"],
  "message": "Success"
}
```

## Add a New Reference (Upload Once)

```bash
curl -X POST http://127.0.0.1:8080/v1/references/add \
  -F "id=my-voice" \
  -F "audio=@voice.wav" \
  -F "text=This is my voice sample"
```

Response:
```json
{
  "success": true,
  "message": "Reference voice 'my-voice' added successfully",
  "reference_id": "my-voice"
}
```

## Use Saved Reference (No Re-upload Needed!)

```bash
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello from Fish Speech!",
    "reference_id": "my-voice",
    "format": "wav"
  }' \
  --output output.wav
```

## Delete a Reference

```bash
curl -X DELETE http://127.0.0.1:8080/v1/references/delete \
  -H "Content-Type: application/json" \
  -d '{"reference_id": "my-voice"}'
```

## Update a Reference

```bash
curl -X POST http://127.0.0.1:8080/v1/references/update \
  -H "Content-Type: application/json" \
  -d '{
    "old_id": "my-voice",
    "new_id": "my-new-voice"
  }'
```

## Multi-Speaker References

For dialogue with multiple speakers, add multiple audio files to the same reference directory:

```bash
# Manually create multi-speaker reference
mkdir -p references/conversation
cp speaker1.wav references/conversation/speaker1.wav
cp speaker2.wav references/conversation/speaker2.wav
echo "Hello, I'm speaker one" > references/conversation/speaker1.lab
echo "Hi, I'm speaker two" > references/conversation/speaker2.lab

# Use it
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "<|speaker:0|>Hello! <|speaker:1|>Hi there!",
    "reference_id": "conversation",
    "format": "wav"
  }' \
  --output dialogue.wav
```

## Where References Are Stored

All references are saved in the `references/` directory:

```
references/
├── my-voice/
│   ├── reference.wav
│   └── reference.lab
├── dialogue/
│   ├── speaker0.wav
│   ├── speaker0.lab
│   ├── speaker1.wav
│   └── speaker1.lab
└── emily/
    ├── happy.wav
    ├── happy.lab
    ├── normal.wav
    └── normal.lab
```

## WebUI Integration

If you're using the Awesome WebUI, it should have a dropdown to select saved references. Check the UI for:
- "Select Reference Voice" dropdown
- "Manage References" button
- List of available reference IDs

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/references/list` | GET | List all saved references |
| `/v1/references/add` | POST | Upload and save a new reference |
| `/v1/references/delete` | DELETE | Delete a saved reference |
| `/v1/references/update` | POST | Rename a reference |
| `/v1/tts` | POST | Generate speech (use `reference_id` field) |

## Python Example

```python
import requests

# List available references
response = requests.get("http://127.0.0.1:8080/v1/references/list")
references = response.json()["reference_ids"]
print("Available references:", references)

# Use a saved reference
response = requests.post(
    "http://127.0.0.1:8080/v1/tts",
    json={
        "text": "Hello from Fish Speech!",
        "reference_id": "my-voice",  # Use saved reference
        "format": "wav",
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

## No Re-upload Needed!

Once you upload a reference with `/v1/references/add`, it's saved permanently in the `references/` directory. You can:

1. ✅ Reuse it anytime with `reference_id`
2. ✅ List all saved references
3. ✅ Delete old references
4. ✅ Rename references
5. ✅ Use multiple references for dialogue

The references persist across server restarts!
