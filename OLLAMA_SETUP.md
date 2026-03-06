# Ollama Offline Mode

This document explains how to use Ollama for offline AI responses when the Gemini API is unavailable or quota is exceeded.

## What is Ollama?

Ollama is a lightweight framework for running Large Language Models (LLMs) locally on your computer. It's completely free and requires no cloud API keys.

**Key Features:**
- ✅ Runs completely offline (no internet required after setup)
- ✅ Free (no API costs)
- ✅ Fast responses with modern hardware
- ✅ Privacy-focused (data stays on your computer)
- ✅ Easy to install and use

## Installation

### Windows

1. **Download Ollama**: https://ollama.ai/download/windows
2. **Install**: Run the installer
3. **Verify**: Open PowerShell and run:
   ```powershell
   ollama --version
   ```

### Mac

1. **Install via HomeBrew**:
   ```bash
   brew install ollama
   ```
2. **Verify**:
   ```bash
   ollama --version
   ```

### Linux

1. **Install**:
   ```bash
   curl https://ollama.ai/install.sh | sh
   ```
2. **Verify**:
   ```bash
   ollama --version
   ```

## Getting Started

### Step 1: Start Ollama Server

**Windows**: Just click the Ollama application icon (it runs in background)

**Mac/Linux**: Open a terminal and run:
```bash
ollama serve
```

You should see:
```
Listening on 127.0.0.1:11434
```

### Step 2: Pull a Model

Open a **new** terminal/PowerShell and pull a model:

```bash
ollama pull mistral
```

Available models to try:
- **mistral** (7B) - Fastest, good quality (recommended)
- **neural-chat** (7B) - Great for conversations
- **llama2** (7B/13B) - More powerful but slower
- **openchat** (3.5B) - Smallest, fastest
- **zephyr** (7B) - Optimized for instructions

### Step 3: Verify Setup

Check available models:
```bash
ollama list
```

Test connectivity:
```bash
curl http://localhost:11434/api/tags
```

You should see a JSON response with available models.

## Using Ollama with HealthBot

### Automatic Fallback

The system **automatically** uses Ollama when:
1. ❌ Gemini API quota is exceeded
2. ❌ Gemini API is unavailable
3. ❌ Internet connection fails
4. ✅ Ollama is running locally

**No code changes needed!** Just start Ollama and it works.

### Manual Testing

Test the Ollama integration:

```bash
python test_ollama.py
```

This will:
- ✅ Check if Ollama is running
- ✅ List available models
- ✅ Test visualization generation
- ✅ Show sample responses

### Using in Your App

The app automatically tries this sequence:
1. **Try Gemini API** (if quota available)
2. **Try Ollama** (if running locally)
3. **Fall back to Demo Mode** (realistic synthetic data)

## Performance & Recommendations

### Model Selection by Hardware

| Model | VRAM | Speed | Quality | Recommended For |
|-------|------|-------|---------|-----------------|
| mistral | 4GB | ⚡⚡⚡ | Good | Most users |
| neural-chat | 4GB | ⚡⚡⚡ | Good | Conversations |
| llama2-7b | 4GB | ⚡⚡ | Better | Good hardware |
| openchat | 2GB | ⚡⚡⚡⚡ | Fair | Low VRAM |
| zephyr | 4GB | ⚡⚡ | Excellent | Best responses |

### Tips for Speed

1. **Use mistral** - Best balance
2. **Keep only one model**: Pull exactly one model to save space
3. **Have 4GB+ RAM available**
4. **Use SSD** - Much faster than HDD
5. **Run on dedicated GPU** (if available) - Significantly faster

## Troubleshooting

### Ollama Command Not Found

**Windows/Mac Issue**: 
- Make sure Ollama is installed and running
- Check: Is the Ollama app open in system tray?

**Linux Issue**:
```bash
sudo systemctl restart ollama
```

### Connection Refused (127.0.0.1:11434)

Ollama is not running!

**Windows**: Click the Ollama icon to start it

**Mac/Linux**: Open terminal and run:
```bash
ollama serve
```

### Downloaded Wrong Model

Remove a model:
```bash
ollama rm mistral
```

### Out of Memory

If models run out of memory:
1. Close other apps
2. Use smaller model: `ollama pull neural-chat`
3. Or upgrade RAM

### Slow Responses

1. Mistral is fastest - use that
2. Check system resources
3. Download model again (corrupted download):
   ```bash
   ollama rm mistral
   ollama pull mistral
   ```

## Code Examples

### Direct Python Usage

```python
from health_app.services.ollama_service import OllamaService

# Check if Ollama is available
if OllamaService.is_ollama_available():
    service = OllamaService(model='mistral')
    
    response = service.generate_response("What is fever?")
    print(response['message'])
    print(f"Visualizations: {len(response['visualizations'])}")
```

### Get Available Models

```python
from health_app.services.ollama_service import OllamaService

models = OllamaService.get_available_models()
print(f"Available: {models}")
```

### Use Different Model

```python
from health_app.services.ollama_service import OllamaService

service = OllamaService(model='neural-chat')
response = service.generate_response("Show me COVID symptoms")
```

## Environment Variables

You can customize Ollama settings:

```bash
# Set Ollama server URL (if not localhost)
export OLLAMA_BASE_URL=http://192.168.1.100:11434

# Set default model
export OLLAMA_MODEL=mistral
```

Then in code:
```python
from health_app.services.ollama_service import OllamaService

service = OllamaService(
    model=os.getenv('OLLAMA_MODEL', 'mistral'),
    base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
)
```

## Comparison: Gemini vs Ollama

| Feature | Gemini | Ollama |
|---------|--------|--------|
| Cost | Free tier (20 req/day) | Free (unlimited) |
| Requires Internet | Yes | No (after download) |
| Setup | Automatic | ~5-10 min |
| Speed | Fast | Medium-Slow |
| Quality | Excellent | Good |
| Custom Models | No | Yes |
| Privacy | Cloud-based | Local only |
| Offline | No | Yes |

## Advanced: Custom Model URL

Connect to Ollama on different machine:

```python
from health_app.services.ollama_service import OllamaService

# Connect to remote Ollama instance
service = OllamaService(
    base_url='http://192.168.1.50:11434'
)
```

## Next Steps

1. ✅ Install Ollama: https://ollama.ai
2. ✅ Start Ollama server
3. ✅ Pull a model: `ollama pull mistral`
4. ✅ Test with: `python test_ollama.py`

That's it! Your app now has offline AI capability!

## Support

For Ollama help: https://github.com/ollama/ollama
For this integration: Check `health_app/services/ollama_service.py`

---

**Happy offline chatting! 🚀**
