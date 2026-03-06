# Quick Test Guide - Ollama Service Improvements

## Summary of Changes

Your Ollama service has been improved with:

✅ **Faster timeout** - Reduced from 120s to 60s for quicker user feedback
✅ **Smarter model selection** - Auto-selects fast models, skips slow ones
✅ **Better error messages** - Specific, helpful error messages with solutions
✅ **Robust response handling** - Handles JSON, plain text, and edge cases
✅ **Detailed logging** - Emoji-based progress indicators for debugging

## Testing Steps

### 1. Start Ollama (if not already running)
```bash
ollama serve
```

### 2. Ensure you have fast models installed
```bash
# Super fast (~100MB, ~1-2 sec response time)
ollama pull phi3:mini

# OR Fast and good quality (~14GB, ~3-5 sec response time)  
ollama pull mistral
```

### 3. Test through web interface
- Open browser to: `http://localhost:8000/chat/` or `http://localhost:8000/course/`
- Try these test queries:

#### Test 1: Normal request
```
"What are common cold symptoms?"
```
Expected: Fast response from Ollama with medical info

#### Test 2: Visualization request
```
"Show me top 10 health tips with a bar chart"
```
Expected: Response with visualization data

#### Test 3: Long request (timeout test)
If using a very large model, it might timeout:
```
"Explain in detail the history of modern medicine with 50+ key points"
```
Expected: If slow model → "Ollama is responding slowly..." message (still helpful!)

## What's Different

### Before Improvements:
```
User asks a question
→ Gemini API (if available) or generic "Error calling Ollama"
→ Not user-friendly or informative
```

### After Improvements:
```
User asks a question
   ↓
✅ Try Gemini first (fast, high quality)
   If quota exceeded...
   ↓
✅ Try Ollama with auto-selected fast model (60s timeout)
   If timeout (slow model)...
   ↓
   "Ollama is responding slowly. Try again (faster second time)"
   If model not found...
   ↓
   "Model not found. Try: ollama pull phi3:mini"
   If not running...
   ↓
   "Cannot connect to Ollama. Is it running at http://localhost:11434?"
   If all else fails...
   ↓
✅ Use Demo Mode with realistic hardcoded data
```

## Debugging Tips

### Check the Django logs while testing:
Look for these indicators in the server output:

```
📤 Calling Ollama (phi3:mini)...        ← Request being sent
📥 Got response (245 chars)             ← Response received  
✅ Successfully parsed Ollama response  ← Success!

OR

⏱️ Ollama timeout (60s)                 ← Model took too long
Cannot connect to Ollama...             ← Service not running
Model not found...                      ← Model needs to be pulled
```

## Performance Metrics

Expected response times with proper models:

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| phi3:mini | 2.7B | 1-3 sec | Good ✅ (RECOMMENDED) |
| mistral | 7B | 3-5 sec | Good+ |
| neural-chat | 7B | 4-6 sec | Good |
| tinyllama | 1B | <1 sec | Fair |
| gemma3:latest | Large | 10-20 sec | Slow ⚠️ |
| llama2:33b+ | Large | 20+ sec | Slow ⚠️ |

## If You Encounter Issues

### Issue: "Cannot connect to Ollama"
**Solution**: Start Ollama server
```bash
ollama serve
```

### Issue: "Model not found" 
**Solution**: Install the model
```bash
ollama pull phi3:mini
```

### Issue: "Ollama is responding slowly"
**Solution**: Either:
- Wait (second attempt is usually faster)
- Install a faster model: `ollama pull phi3:mini`
- Check system resources (RAM, CPU)

### Issue: Still getting generic errors
**Solution**: Check the Django logs for detailed error info. The improved logging should show:
- Exact error code
- Which endpoint was tried
- What the model returned

## Testing the Fallback Chain

The system has 3 tiers of fallback:

```python
# Tier 1: Gemini API (current quota: 20 requests/day)
Try Gemini → 
   If 429 quota error →
   
# Tier 2: Ollama (now with improvements!)
   Try Ollama (60s timeout, smart model selection) →  
   If Ollama not available or error →
   
# Tier 3: Demo Mode
   Return realistic hardcoded visualizations
```

Each tier gets better error messages and logging, making it easier to diagnose issues.

## Files Modified

- `health_app/services/ollama_service.py` - Improved with:
  - Timeout: 120s → 60s
  - Model selection: Smart fast model preference
  - Error messages: Specific, helpful messages
  - Response handling: JSON + plain text fallback
  
- `health_app/views.py` - Already had fallback logic, now works better!

## Next Steps

1. Test with the queries above
2. Monitor Django logs for emoji indicators
3. Report any specific error messages in logs
4. Adjust timeout if needed (currently 60s)
5. Can always reduce to 45s or increase to 90s if needed
