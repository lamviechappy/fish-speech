# Running Fish Speech API Server on Mac Mini

## Quick Start (MLX Backend - Recommended)

### 1. Activate the conda environment
```bash
conda activate fish
```

### 2. Start the API server with MLX backend
```bash
cd /Volumes/WD500/dev/fishaudio

# Basic command (uses default settings)
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx

# With custom port and host
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --listen 0.0.0.0:8080

# With API key for security
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --api-key your-secret-key-here

# With compilation enabled (faster inference)
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile
```

### 3. Server will start and show:
```
INFO     Loading MLX inference engine...
INFO     MLX inference engine loaded.
INFO     Warming up model...
INFO     Models warmed up.
INFO     Startup done, listening server at http://127.0.0.1:8080
```

### 4. Test the API

**Using curl:**
```bash
curl -X POST http://127.0.0.1:8080/v1/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello from Fish Speech!",
    "format": "wav"
  }' \
  --output test.wav
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://127.0.0.1:8080/v1/tts",
    json={
        "text": "Hello from Fish Speech!",
        "format": "wav",
        "chunk_length": 200,
        "top_p": 0.7,
        "temperature": 0.7,
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--backend` | `mlx` | Backend to use: `mlx` or `pytorch` |
| `--llama-checkpoint-path` | `checkpoints/s2-pro` | Model path or HuggingFace ID |
| `--decoder-checkpoint-path` | `checkpoints/s2-pro/codec.pth` | Decoder path (PyTorch only) |
| `--decoder-config-name` | `modded_dac_vq` | Decoder config (PyTorch only) |
| `--device` | `cuda` | Device (PyTorch only, ignored for MLX) |
| `--half` | `False` | Use half precision (PyTorch only) |
| `--compile` | `False` | Enable compilation for faster inference |
| `--listen` | `127.0.0.1:8080` | Host and port to listen on |
| `--workers` | `1` | Number of worker processes |
| `--api-key` | `None` | API key for authentication |
| `--max-text-length` | `0` | Max text length (0 = unlimited) |

## Recommended Settings for Mac Mini

### For Local Development
```bash
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile \
  --listen 127.0.0.1:8080
```

### For Network Access (accessible from other devices)
```bash
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile \
  --listen 0.0.0.0:8080 \
  --api-key your-secret-key
```

### For Production (with security)
```bash
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile \
  --listen 0.0.0.0:8080 \
  --api-key $(cat ~/.fish-api-key) \
  --workers 2
```

## API Endpoints

### POST /v1/tts
Generate speech from text.

**Request body:**
```json
{
  "text": "Hello world!",
  "references": [],
  "reference_id": null,
  "max_new_tokens": 1024,
  "chunk_length": 200,
  "top_p": 0.7,
  "repetition_penalty": 1.2,
  "temperature": 0.7,
  "format": "wav",
  "streaming": false
}
```

**Response:**
- Audio file (WAV/MP3/FLAC/OPUS depending on format)

### GET /docs
OpenAPI documentation (Swagger UI)

### GET /openapi.json
OpenAPI specification

## Running in Background

### Using screen
```bash
screen -S fish-api
conda activate fish
python tools/api_server.py --llama-checkpoint-path mlx-community/fish-audio-s2-pro --backend mlx --compile
# Press Ctrl+A, then D to detach
# Reattach with: screen -r fish-api
```

### Using tmux
```bash
tmux new -s fish-api
conda activate fish
python tools/api_server.py --llama-checkpoint-path mlx-community/fish-audio-s2-pro --backend mlx --compile
# Press Ctrl+B, then D to detach
# Reattach with: tmux attach -t fish-api
```

### Using nohup
```bash
nohup python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile \
  > api_server.log 2>&1 &

# Check logs
tail -f api_server.log

# Stop server
pkill -f api_server.py
```

## Connecting WebUI to API Server

If you want to run the WebUI separately and connect it to the API server:

**Terminal 1 (API Server):**
```bash
conda activate fish
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile \
  --listen 0.0.0.0:8080
```

**Terminal 2 (WebUI):**
```bash
conda activate fish
python tools/run_webui.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile
```

## Troubleshooting

### Model not found
If you get "model not found", the model will be downloaded automatically on first run. This takes a few minutes (~10GB download).

### Port already in use
```bash
# Check what's using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>

# Or use a different port
python tools/api_server.py --listen 127.0.0.1:8081 ...
```

### Memory issues
If you run out of memory, try:
- Close other applications
- Use a quantized model (smaller size)
- Reduce `--workers` to 1

### Slow first request
The first request will be slower as the model loads and compiles. Subsequent requests will be much faster.

## Performance Tips

1. **Enable compilation**: `--compile` flag enables MLX JIT compilation for faster inference
2. **Use MLX backend**: Much faster than PyTorch on Apple Silicon
3. **Keep server running**: Avoid restarting to keep model in memory
4. **Adjust chunk_length**: Smaller chunks = faster response, larger chunks = better quality
5. **Monitor memory**: Use Activity Monitor to check memory usage

## Next Steps

- Check `RUNNING_WEBUI.md` for WebUI setup (Gradio and Awesome WebUI)
- Check `MLX_INTEGRATION.md` for more details on MLX backend
- Check `MODEL_DISTRIBUTION.md` for app distribution strategies
- Visit http://127.0.0.1:8080/docs for interactive API documentation
