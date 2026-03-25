# Running Fish Speech with Awesome WebUI

## Overview

Fish Speech has two web interfaces:
1. **Gradio WebUI** - Simple Python-based interface
2. **Awesome WebUI** - Modern TypeScript interface with better UX (recommended)

This guide covers both, with focus on Awesome WebUI.

---

## Option 1: Awesome WebUI (Recommended)

Awesome WebUI is a modernized web interface built with TypeScript, offering richer features and a better user experience.

### Prerequisites

- Node.js (v16 or higher)
- npm (comes with Node.js)
- Conda environment with Fish Speech installed

### Step 1: Build the Awesome WebUI

```bash
cd /Volumes/WD500/dev/fishaudio

# Enter the awesome_webui directory
cd awesome_webui

# Install dependencies
npm install

# Build the WebUI
npm run build
```

This will create a production build in the `dist/` directory.

### Step 2: Start the API Server

The Awesome WebUI connects to the API server, so you need to start it first.

**Terminal 1 - API Server:**
```bash
cd /Volumes/WD500/dev/fishaudio
conda activate fish

# Start API server with MLX backend
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile \
  --listen 0.0.0.0:8080
```

Wait until you see:
```
INFO     Startup done, listening server at http://0.0.0.0:8080
```

### Step 3: Serve the Awesome WebUI

**Terminal 2 - WebUI:**
```bash
cd /Volumes/WD500/dev/fishaudio/awesome_webui

# Option A: Using npm (development mode with hot reload)
npm run dev

# Option B: Using a simple HTTP server (production build)
npx serve dist -p 3000

# Option C: Using Python's HTTP server
python3 -m http.server 3000 -d dist
```

### Step 4: Access the WebUI

Open your browser and go to:
```
http://localhost:3000
```

Or if you used `npm run dev`:
```
http://localhost:5173
```

### Step 5: Configure API Endpoint

In the Awesome WebUI:
1. Look for Settings or Configuration
2. Set API endpoint to: `http://localhost:8080`
3. If you set an API key, enter it here

---

## Option 2: Gradio WebUI (Simple)

The Gradio WebUI is simpler and runs everything in one process.

### Start Gradio WebUI

```bash
cd /Volumes/WD500/dev/fishaudio
conda activate fish

# Start with MLX backend
python tools/run_webui.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile
```

### Access Gradio WebUI

The WebUI will automatically open in your browser, or go to:
```
http://127.0.0.1:7860
```

---

## Comparison: Awesome WebUI vs Gradio WebUI

| Feature | Awesome WebUI | Gradio WebUI |
|---------|---------------|--------------|
| **Technology** | TypeScript + React | Python + Gradio |
| **UI/UX** | Modern, polished | Simple, functional |
| **Setup** | Requires build step | No build needed |
| **Architecture** | Separate API + UI | All-in-one |
| **Customization** | Highly customizable | Limited |
| **Performance** | Better for production | Good for development |
| **Hot Reload** | Yes (dev mode) | No |

---

## Recommended Setup for Mac Mini

### For Development

**Terminal 1 - API Server:**
```bash
cd /Volumes/WD500/dev/fishaudio
conda activate fish
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile \
  --listen 127.0.0.1:8080
```

**Terminal 2 - Awesome WebUI (Dev Mode):**
```bash
cd /Volumes/WD500/dev/fishaudio/awesome_webui
npm run dev
```

Access at: http://localhost:5173

### For Production / Network Access

**Terminal 1 - API Server:**
```bash
cd /Volumes/WD500/dev/fishaudio
conda activate fish
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile \
  --listen 0.0.0.0:8080 \
  --api-key your-secret-key
```

**Terminal 2 - Awesome WebUI (Production):**
```bash
cd /Volumes/WD500/dev/fishaudio/awesome_webui
npm run build
npx serve dist -p 3000 -s
```

Access from any device on your network:
```
http://<mac-mini-ip>:3000
```

---

## Running in Background

### Using tmux (Recommended)

**Start both services:**
```bash
# Create a new tmux session
tmux new -s fish

# Start API server in first pane
conda activate fish
cd /Volumes/WD500/dev/fishaudio
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile \
  --listen 0.0.0.0:8080

# Split window (Ctrl+B, then ")
# In the new pane, start WebUI
cd /Volumes/WD500/dev/fishaudio/awesome_webui
npx serve dist -p 3000

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t fish
```

### Using screen

**Terminal 1 - API Server:**
```bash
screen -S fish-api
conda activate fish
cd /Volumes/WD500/dev/fishaudio
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile
# Detach: Ctrl+A, then D
```

**Terminal 2 - WebUI:**
```bash
screen -S fish-webui
cd /Volumes/WD500/dev/fishaudio/awesome_webui
npx serve dist -p 3000
# Detach: Ctrl+A, then D
```

**Reattach:**
```bash
screen -r fish-api
screen -r fish-webui
```

---

## Awesome WebUI Development

### Development Mode (with hot reload)

```bash
cd /Volumes/WD500/dev/fishaudio/awesome_webui

# Start dev server
npm run dev

# The dev server will watch for changes and auto-reload
```

### Build for Production

```bash
cd /Volumes/WD500/dev/fishaudio/awesome_webui

# Build optimized production bundle
npm run build

# Preview the production build
npm run preview
```

### Project Structure

```
awesome_webui/
├── src/              # Source code
│   ├── components/   # React components
│   ├── pages/        # Page components
│   ├── api/          # API client
│   └── main.tsx      # Entry point
├── public/           # Static assets
├── dist/             # Production build (generated)
├── package.json      # Dependencies
├── vite.config.ts    # Vite configuration
└── tsconfig.json     # TypeScript configuration
```

---

## Troubleshooting

### Port conflicts

**If port 8080 is in use:**
```bash
# Find what's using the port
lsof -i :8080

# Use a different port
python tools/api_server.py --listen 127.0.0.1:8081 ...
```

**If port 3000 is in use:**
```bash
# Use a different port for WebUI
npx serve dist -p 3001
```

### API connection issues

1. Check API server is running: `curl http://localhost:8080/docs`
2. Check WebUI API endpoint setting matches server address
3. Check firewall settings if accessing from another device
4. Check CORS settings in API server

### Build errors

```bash
# Clear node_modules and reinstall
cd awesome_webui
rm -rf node_modules package-lock.json
npm install

# Clear build cache
rm -rf dist
npm run build
```

### Model loading issues

First request will be slow as model downloads (~10GB). Check:
```bash
# Check if model is cached
ls -la ~/.cache/huggingface/hub/models--mlx-community--fish-audio-s2-pro/

# Monitor download progress in API server logs
```

---

## Performance Tips

1. **Use MLX backend** - Much faster on Apple Silicon
2. **Enable compilation** - Add `--compile` flag
3. **Keep services running** - Avoid restarting to keep model in memory
4. **Use production build** - `npm run build` is faster than dev mode
5. **Adjust chunk_length** - Balance between speed and quality

---

## Quick Start Commands

### All-in-One (Gradio WebUI)
```bash
conda activate fish
cd /Volumes/WD500/dev/fishaudio
python tools/run_webui.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile
```

### Awesome WebUI (Two terminals)
```bash
# Terminal 1
conda activate fish
cd /Volumes/WD500/dev/fishaudio
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro \
  --backend mlx \
  --compile

# Terminal 2
cd /Volumes/WD500/dev/fishaudio/awesome_webui
npm run dev
```

---

## Next Steps

- Check `RUNNING_API_SERVER.md` for detailed API server configuration
- Check `MLX_INTEGRATION.md` for MLX backend details
- Check `MODEL_DISTRIBUTION.md` for app distribution strategies
- Visit http://localhost:8080/docs for API documentation
