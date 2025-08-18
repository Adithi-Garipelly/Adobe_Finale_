# Document Insight & Engagement System
A sophisticated PDF analysis platform that uses Adobe PDF Embed API, AI insights, and podcast generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- Adobe PDF Embed API Key (free from Adobe)

### 1. Clone/Download Project
```bash
git clone https://github.com/Adithi-Garipelly/Adobe_Finale_.git
cd Adobe_Finale_
```

### 2. Set Up Environment Variables
Create `frontend/.env` file:
```env
REACT_APP_API=http://localhost:8000
REACT_APP_ADOBE_EMBED_API_KEY=YOUR_API_KEY_HERE
```

### 3. Install Dependencies
```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 4. Run the System
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm start
```

### 5. Open in Browser
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📱 How to Use

1. **Upload PDFs** - Select multiple PDF files (up to 50)
2. **View Library** - See all uploaded PDFs
3. **Open PDF** - Click "Open" on any file to view in Adobe PDF Embed API
4. **Select Text** - Highlight text in PDF or paste manually
5. **Generate Insights** - Get AI analysis with relevant sections and insights
6. **Create Podcast** - Generate audio + transcript using Azure TTS

## 🔧 Features

- ✅ Multiple PDF upload and management (up to 50 files)
- ✅ Adobe PDF Embed API (no iframes)
- ✅ AI-powered text analysis with Gemini 2.5 Flash
- ✅ Cross-document insights and semantic search
- ✅ Podcast generation with Azure TTS
- ✅ FAISS vector search with sentence transformers
- ✅ Clean, modern UI with page-based navigation

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI + Uvicorn
- **Frontend**: React + Axios
- **PDF Viewer**: Adobe PDF Embed API
- **AI**: Google Gemini 2.5 Flash
- **TTS**: Azure Cognitive Services
- **Search**: FAISS + Sentence Transformers
- **PDF Processing**: pdfminer.six

## 📁 Project Structure

```
Adobe_Finale_/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app with new endpoints
│   │   ├── search_index.py  # FAISS-based semantic search
│   │   ├── insights.py      # AI insights generation
│   │   ├── llm_adapter.py   # Gemini integration
│   │   └── tts.py          # Azure TTS integration
│   ├── requirements.txt
│   └── data/                # Uploaded PDFs
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── UploadPage.js    # File upload (up to 50)
│   │   │   ├── LibraryPage.js   # File library
│   │   │   └── ViewerPage.js    # PDF viewer + insights
│   │   └── App.js          # Main app with page routing
│   ├── package.json
│   └── .env                 # Environment variables
└── README.md
```

## 🚨 Troubleshooting

### Adobe PDF Viewer Not Loading
- Check `.env` file has correct API key
- Restart frontend after changing `.env`
- Check browser console for errors

### Backend Not Starting
- Ensure Python 3.10+ is installed
- Check if port 8000 is available
- Verify all dependencies are installed

### Frontend Not Starting
- Ensure Node.js 16+ is installed
- Check if port 3000 is available
- Verify all npm packages are installed

## 📞 Support

If you encounter issues:
1. Check browser console (F12)
2. Check terminal output
3. Verify environment variables
4. Ensure all dependencies are installed

## 🎯 Project Goals

This system demonstrates:
- Modern web development with React + FastAPI
- Adobe PDF Embed API integration
- AI-powered document analysis with Gemini
- Cross-document insights generation
- Podcast creation from text with Azure TTS
- Professional UI/UX design

## 🔄 Recent Updates

- **Improved Backend**: New FAISS-based semantic search with better sectioning
- **Enhanced Frontend**: Page-based navigation with upload, library, and viewer
- **Better PDF Handling**: Support for up to 50 files with improved indexing
- **Robust Text Selection**: Adobe PDF Embed API with manual fallback
- **Structured Insights**: AI-generated analysis with relevant sections
- **Azure TTS Integration**: High-quality podcast generation

Happy coding! 🚀
