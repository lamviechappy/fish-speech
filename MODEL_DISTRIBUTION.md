# Model Storage and Distribution Guide

## Where Models Are Stored

### Default Cache Location

When you use `load_model("mlx-community/fish-audio-s2-pro")`, the model is downloaded to:

```
~/.cache/huggingface/hub/models--mlx-community--fish-audio-s2-pro/
```

Or on your external drive:
```
/Volumes/WD500/.cache/huggingface/hub/models--mlx-community--fish-audio-s2-pro/
```

**Model Size**: ~10GB (includes model weights, codec, tokenizer, config)

### How It Works

1. `mlx_audio.tts.utils.load()` calls `get_model_path()`
2. `get_model_path()` checks if path exists locally
3. If not found, calls `huggingface_hub.snapshot_download()`
4. Downloads to `HF_HUB_CACHE` (default: `~/.cache/huggingface/hub/`)
5. Creates symlinks in `snapshots/` pointing to `blobs/`

## For App Distribution (Fish Audio.app / Fish Audio.dmg)

You have **two main options**:

### Option 1: Bundle Models Inside the App (Recommended for Standalone App)

**Pros:**
- Users don't need to download anything
- Works offline immediately
- Predictable app size
- No network dependency on first launch

**Cons:**
- Large app size (~10GB + app code)
- Updates require full app redownload
- Takes up space even if user doesn't use it

**Implementation:**

```python
# In your app code
import os
from pathlib import Path

# Get the app bundle path
if getattr(sys, 'frozen', False):
    # Running as bundled app
    bundle_dir = Path(sys._MEIPASS)  # PyInstaller
    # or
    bundle_dir = Path(os.path.dirname(sys.executable)).parent / "Resources"  # py2app
else:
    # Running as script
    bundle_dir = Path(__file__).parent

# Model path inside app bundle
model_path = bundle_dir / "models" / "fish-audio-s2-pro"

# Load from bundled path
from mlx_audio.tts.utils import load_model
engine = MLXTTSInferenceEngine(
    llama_checkpoint_path=str(model_path),
    compile=True,
)
```

**Directory structure:**
```
Fish Audio.app/
├── Contents/
│   ├── MacOS/
│   │   └── fish-audio (executable)
│   ├── Resources/
│   │   └── models/
│   │       └── fish-audio-s2-pro/
│   │           ├── config.json
│   │           ├── model-00001-of-00002.safetensors
│   │           ├── model-00002-of-00002.safetensors
│   │           ├── codec.safetensors
│   │           ├── tokenizer.json
│   │           └── ...
│   └── Info.plist
```

### Option 2: Download on First Launch (Recommended for Lightweight Distribution)

**Pros:**
- Small initial download (~50MB app)
- Easy to update models separately
- Users only download what they need
- Can offer multiple model options

**Cons:**
- Requires internet on first launch
- Slower first-time experience
- Need to handle download progress/errors

**Implementation:**

```python
import os
from pathlib import Path
from mlx_audio.tts.utils import load_model

# Set custom cache directory inside app support
app_support = Path.home() / "Library" / "Application Support" / "Fish Audio"
app_support.mkdir(parents=True, exist_ok=True)

# Option A: Use HuggingFace cache (standard location)
# Models go to ~/.cache/huggingface/hub/
engine = MLXTTSInferenceEngine(
    llama_checkpoint_path="mlx-community/fish-audio-s2-pro",
    compile=True,
)

# Option B: Use custom cache location
os.environ['HF_HOME'] = str(app_support / "models")
engine = MLXTTSInferenceEngine(
    llama_checkpoint_path="mlx-community/fish-audio-s2-pro",
    compile=True,
)
```

**With progress UI:**

```python
from huggingface_hub import snapshot_download
from tqdm import tqdm

def download_model_with_progress(model_id: str, cache_dir: Path):
    """Download model with progress bar."""
    print(f"Downloading {model_id}...")

    model_path = snapshot_download(
        model_id,
        cache_dir=cache_dir,
        resume_download=True,
        # Add progress callback if needed
    )

    return model_path

# Check if model exists
model_id = "mlx-community/fish-audio-s2-pro"
cache_dir = app_support / "models"

# Download if not cached
if not (cache_dir / f"models--{model_id.replace('/', '--')}").exists():
    download_model_with_progress(model_id, cache_dir)

# Load model
engine = MLXTTSInferenceEngine(
    llama_checkpoint_path=model_id,
    compile=True,
)
```

### Option 3: Hybrid Approach (Best User Experience)

**Bundle a quantized model + download full model on demand:**

```python
# Bundle 4-bit quantized model (~2.5GB) in app
bundled_model = bundle_dir / "models" / "fish-audio-s2-pro-4bit"

# Offer full model as optional download
full_model = "mlx-community/fish-audio-s2-pro"

# Let user choose in settings
if user_preference == "quality":
    model_path = full_model  # Download 10GB model
else:
    model_path = str(bundled_model)  # Use bundled 4-bit
```

## Recommended Approach for Fish Audio.app

**For initial release:**

1. **Use Option 2** (download on first launch)
2. Store models in `~/Library/Application Support/Fish Audio/models/`
3. Show a nice progress UI during first launch
4. Cache models so subsequent launches are instant

**Why this is better:**

- **Smaller DMG**: ~50MB vs ~10GB
- **Faster downloads**: Users download from HuggingFace CDN
- **Easy updates**: Just update the app, models stay cached
- **Multiple models**: Users can switch between models without reinstalling
- **Standard practice**: Most AI apps work this way (Whisper, Stable Diffusion, etc.)

**Example first-launch flow:**

```
1. User opens Fish Audio.app
2. App checks: ~/.cache/huggingface/hub/models--mlx-community--fish-audio-s2-pro/
3. If not found:
   - Show dialog: "Downloading Fish Speech model (10GB)..."
   - Show progress bar
   - Download to cache
4. Load model and start app
5. Next launch: instant (model already cached)
```

## Model Locations Summary

| Location | Use Case | Size |
|----------|----------|------|
| `~/.cache/huggingface/hub/` | Default HuggingFace cache | 10GB |
| `~/Library/Application Support/Fish Audio/models/` | Custom app cache | 10GB |
| `Fish Audio.app/Contents/Resources/models/` | Bundled in app | 10GB |
| Project folder (`checkpoints/`) | Development only | 10GB |

## Recommendation

**For Fish Audio.app distribution:**

✅ **Use `~/.cache/huggingface/hub/` (Option 2)**
- Standard location that all HuggingFace tools use
- Shared across apps (if user has other HF apps)
- Easy to clear cache if needed
- No custom path management

✅ **Use official model: `mlx-community/fish-audio-s2-pro`**
- Not the `-bf16` variant
- This is the standard MLX conversion

✅ **Show download progress on first launch**
- Better UX than silent download
- Let users know what's happening

❌ **Don't bundle models in DMG**
- Makes DMG too large (10GB+)
- Slow to download and install
- Hard to update

## Code Example for Your App

```python
from pathlib import Path
from mlx_audio.tts.utils import load_model
from fish_speech.inference_engine.mlx_engine import MLXTTSInferenceEngine

def initialize_engine():
    """Initialize MLX engine with automatic model download."""
    model_id = "mlx-community/fish-audio-s2-pro"

    # Check if model is cached
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    model_cache = cache_dir / f"models--{model_id.replace('/', '--')}"

    if not model_cache.exists():
        print(f"First launch: downloading {model_id} (~10GB)...")
        print("This will only happen once.")
        # Show progress UI here

    # Load model (downloads if needed)
    engine = MLXTTSInferenceEngine(
        llama_checkpoint_path=model_id,
        compile=True,
    )

    return engine
```

This way, your Fish Audio.app will be lightweight, fast to distribute, and easy to update!
