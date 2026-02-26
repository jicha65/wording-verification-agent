# 🇨🇳 中国用户安装指南 - China Setup Guide

For China users, the **best solution** is **Ollama** with local AI models. No VPN needed, no API costs, completely offline!

---

## 🚀 快速开始 - Quick Start (5 minutes)

### Step 1: Install Ollama (安装 Ollama)
1. Download from: https://ollama.ai
2. Run installer
3. Ollama will start automatically

### Step 2: Download a Model (下载模型)

**Option A: Mistral (Recommended - Fast, Good Quality)**
```bash
ollama pull mistral
```

**Option B: Llama2 (Larger, Better Quality)**
```bash
ollama pull llama2
```

### Step 3: Start Ollama Service (启动 Ollama)

Keep Ollama running in background:
```bash
ollama serve
```

(Leave this window open while using the app)

### Step 4: Use Streamlit App (使用 Streamlit 应用)

1. Open your Streamlit app
2. Go to **Sidebar → AI Settings**
3. Click **"🖥️ Local AI (Ollama)"** section
4. Click **"🔄 Connect to Ollama"** button
5. See: ✅ Connected!

---

## ✨ Features (功能)

✅ **Works Offline** - 完全离线工作
✅ **No API costs** - 完全免费
✅ **Privacy** - 数据不上传
✅ **Fast** - 快速处理
✅ **Chinese optimized** - 针对中国优化

---

## 📊 Model Comparison (模型对比)

| Model | Speed | Quality | Memory | Language |
|-------|-------|---------|--------|----------|
| **Mistral** | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Good | 5GB | English/Chinese |
| **Llama2** | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Best | 7GB | English/Chinese |
| **Neural Chat** | ⚡⚡⚡⭐ Very Fast | ⭐⭐⭐⭐ Great | 4GB | English |

**Recommendation: Start with Mistral** - Best balance of speed and quality

---

## 🔧 Installation Details (详细安装步骤)

### Windows 用户

1. Download from https://ollama.ai
2. Run `OllamaSetup.exe`
3. Accept installation
4. Restart computer (if prompted)
5. Ollama runs automatically on startup

### Mac 用户

1. Download from https://ollama.ai
2. Drag Ollama.app to Applications
3. Open Applications → Ollama
4. Will run automatically

### Linux 用户

```bash
curl https://ollama.ai/install.sh | sh
ollama serve
```

---

## 🎯 Downloading Models

### Download Mistral (推荐)
```bash
ollama pull mistral
```
Size: ~5GB
Download time: 5-15 minutes (depending on internet)

### Check Downloaded Models
```bash
ollama list
```

Output example:
```
NAME                INSIDES
mistral:latest      4.5GB
```

---

## 🚀 Running Ollama

### Start Service
```bash
ollama serve
```

This keeps running. You should see:
```
2024/02/26 14:30:12 "GET /tags HTTP/1.1" 200
listening on localhost:11434
```

### Keep It Running

- **Windows**: Closes when computer sleeps - restart with `ollama serve`
- **Mac**: Runs continuously after opening the app
- **Linux**: Run in tmux or screen for persistent service

---

## 🎨 Using in Streamlit

### Connect to Ollama
1. Open app sidebar
2. Go to "🤖 AI Settings"
3. Open "🖥️ Local AI (Ollama)"
4. Click "🔄 Connect to Ollama"
5. Wait for connection ✅

### How It Works
- Mistral: ~3-5 seconds per verification
- Llama2: ~5-8 seconds per verification

Much faster than cloud APIs!

---

## 📊 Performance on Different Hardware

**Good (Recommended):**
- Intel i5/i7 or Apple M1+
- 8GB+ RAM
- SSD recommended

**Acceptable:**
- Intel i3 or older
- 6GB RAM
- Slower but works

**Not Recommended:**
- <4GB RAM
- Very old CPU

---

## 🆘 Troubleshooting

### "Ollama not responding" Error
**Solution:**
1. Make sure `ollama serve` is running
2. Check: http://localhost:11434/api/tags
3. Should show your models

### "No models found" Error
**Solution:**
```bash
ollama pull mistral
```

### App runs slowly
**Solution:**
- Close other apps
- Try Mistral instead of Llama2
- Check internet connection (just for first download)

### Connection refused
**Solution:**
1. Open terminal/cmd
2. Run: `ollama serve`
3. Leave it running
4. Refresh Streamlit app

---

## 🆕 Alternative: Google Gemini (Google Gemini 备选方案)

If Ollama doesn't work, you can use free Google Gemini API:

1. Go to: https://ai.google.dev
2. Click "Get API Key"
3. Sign in with Google account
4. Generate key
5. Copy key
6. Paste in Streamlit app

This is also free with generous limits!

---

## 💡 Best Practices

1. **Always keep Ollama running** when using the app
2. **Use Mistral for speed**, Llama2 for quality
3. **Download models once** - reuse indefinitely
4. **Monitor system performance** if running many verifications

---

## 📚 Resources

- **Ollama Official:** https://ollama.ai
- **Model Library:** https://ollama.ai/library
- **Documentation:** https://ollama.ai/docs
- **GitHub Issues:** https://github.com/jmorganca/ollama/issues

---

## 🎉 Success!

Once Ollama is connected, your wording verification agent now has:

✅ AI-powered semantic analysis
✅ Works completely offline
✅ Zero API costs
✅ Complete privacy
✅ Lightning fast responses

Happy verifying! 🚀

---

## 更新 Updates

If you want to switch to a different model:

```bash
# Download new model
ollama pull llama2

# List all models
ollama list

# Use different model
# In Streamlit: Disconnect, reconnect (will auto-detect new models)
```

---

**Last Updated:** February 26, 2026
**Version:** 1.0 - China Optimized
