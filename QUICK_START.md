# 🚀 Adobe Finale - Quick Start

## ✅ What's Fixed

1. **Backend Import Issues** - Resolved module import problems
2. **Podcast Generation** - Fixed Azure TTS failures with fallback audio
3. **Reliable Startup** - Created bulletproof startup scripts

## 🚀 Quick Start (2 Commands)

```bash
# 1. Start everything (backend + frontend)
./start_everything.sh

# 2. Open in browser
open http://localhost:3000
```

## 🔧 Manual Start (if needed)

```bash
# Backend only
./start_backend.sh

# Frontend only  
cd frontend && npm start
```

## 🎯 How to Use

1. **Upload PDFs** - Drag & drop multiple PDFs
2. **View PDFs** - Click on any uploaded PDF
3. **Select Text** - Highlight text in the PDF viewer
4. **Analyze** - Click "Analyze Selection" for insights
5. **Generate Podcast** - Click "Create Podcast" for audio summary

## 🌐 URLs

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8080
- **Health Check**: http://localhost:8080/health

## 📝 Troubleshooting

If something breaks:
```bash
# Restart everything
./start_everything.sh

# Check logs
tail -f backend.log
tail -f frontend.log
```

## 🎉 Features Working

✅ PDF Upload & Storage  
✅ PDF Viewer (Adobe Embed API)  
✅ Text Selection & Analysis  
✅ AI Insights Generation  
✅ Podcast Generation (Azure TTS + Fallback)  
✅ Multi-speaker Audio  
✅ File Serving  

**The application is now fully functional!** 🎊
