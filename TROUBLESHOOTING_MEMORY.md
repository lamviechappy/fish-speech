# Troubleshooting Memory Issues

## Common Memory Errors

### 1. Out of Memory (OOM)

**Symptoms:**
- Server crashes during generation
- Error: "Cannot allocate memory"
- System becomes unresponsive

**Solutions:**

```bash
# Check memory usage
top -l 1 | grep PhysMem

# Monitor during generation
watch -n 1 'ps aux | grep python'
```

**Fixes:**
- Reduce `max_new_tokens` (default: 1024 → try 512)
- Reduce `chunk_length` (default: 300 → try 200)
- Close other applications
- Use quantized model (4-bit or 8-bit)

### 2. MLX Memory Issues

**Error:** "MLX memory allocation failed"

**Solution:**
```python
# Add memory cleanup in mlx_engine.py
import mlx.core as mx
mx.metal.clear_cache()  # Clear MLX memory cache
gc.collect()  # Python garbage collection
```

### 3. Model Loading Issues

**Error:** "Failed to load model weights"

**Solution:**
```bash
# Check available disk space
df -h ~/.cache/huggingface/hub/

# Re-download model if corrupted
rm -rf ~/.cache/huggingface/hub/models--mlx-community--fish-audio-s2-pro
```

### 4. Reference Audio Memory

**Error:** "Memory error when loading reference audio"

**Solution:**
- Limit reference audio length (< 30 seconds recommended)
- Use mono audio (not stereo)
- Reduce sample rate if needed

## Memory Requirements

| Component | Memory Usage |
|-----------|--------------|
| Model (loaded) | ~10GB |
| Inference (peak) | ~12-14GB |
| Reference audio | ~100MB per file |
| Generated audio | ~50MB per minute |

## Recommended System

- **Minimum**: 16GB RAM (M1/M2/M3)
- **Recommended**: 24GB+ RAM (M1 Pro/Max, M2 Pro/Max, M3 Pro/Max)
- **Optimal**: 32GB+ RAM (M1 Max/Ultra, M2 Max/Ultra, M3 Max)

## Memory Optimization Tips

### 1. Reduce Batch Size

```python
# In mlx_engine.py, reduce chunk_length
chunk_length = 200  # Instead of 300
```

### 2. Clear Cache Between Requests

```python
# Add to mlx_engine.py after generation
import mlx.core as mx
mx.metal.clear_cache()
gc.collect()
```

### 3. Use Quantized Model

```bash
# Use 4-bit quantized model (smaller memory footprint)
python tools/api_server.py \
  --llama-checkpoint-path mlx-community/fish-audio-s2-pro-4bit \
  --backend mlx
```

### 4. Limit Concurrent Requests

```bash
# Set workers to 1 (default)
python tools/api_server.py \
  --workers 1 \
  --backend mlx
```

## Monitoring Memory

### Check System Memory

```bash
# macOS
vm_stat | perl -ne '/page size of (\d+)/ and $size=$1; /Pages\s+([^:]+)[^\d]+(\d+)/ and printf("%-16s % 16.2f Mi\n", "$1:", $2 * $size / 1048576);'

# Or use Activity Monitor
open -a "Activity Monitor"
```

### Check MLX Memory

```python
import mlx.core as mx
print(f"MLX memory: {mx.metal.get_active_memory() / 1024**3:.2f} GB")
print(f"MLX peak: {mx.metal.get_peak_memory() / 1024**3:.2f} GB")
```

### Monitor During Generation

```bash
# Terminal 1: Run server
python tools/api_server.py --backend mlx

# Terminal 2: Monitor memory
watch -n 1 'ps aux | grep python | grep -v grep'
```

## If You Still Get Errors

Please share:
1. **Full error message** (copy the entire traceback)
2. **System specs** (Mac model, RAM amount)
3. **What you were doing** (generating with/without references, text length)
4. **Memory usage** (from Activity Monitor or `top`)

This will help me diagnose the specific issue!
