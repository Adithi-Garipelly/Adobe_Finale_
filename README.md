# Document Insight & Engagement System

A sophisticated PDF analysis platform that uses Adobe PDF Embed API, AI insights, and podcast generation.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 16+
- Adobe PDF Embed API Key (free from Adobe)

### 1. Clone/Download Project
```bash
git clone https://github.com/YOUR_USERNAME/adobe-finale.git
cd adobe-finale
```

### 2. Set Up Environment Variables
Create `frontend/.env` file:
```env
REACT_APP_ADOBE_EMBED_API_KEY=YOUR_API_KEY_HERE
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_BACKEND_URL=http://localhost:8000
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

1. **Upload PDFs** - Select multiple PDF files
2. **View PDFs** - Click "View" on any uploaded file
3. **Select Text** - Highlight text in PDF or paste manually
4. **Generate Insights** - Get AI analysis with 5 structured sections
5. **Create Podcast** - Generate audio + transcript

## 🔧 Features

- ✅ Multiple PDF upload and management
- ✅ Adobe PDF Embed API (no iframes)
- ✅ AI-powered text analysis
- ✅ Cross-document insights
- ✅ Podcast generation with Azure TTS
- ✅ Semantic search with FAISS
- ✅ Clean, modern UI

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI + Uvicorn
- **Frontend**: React + Styled Components
- **PDF Viewer**: Adobe PDF Embed API
- **AI**: Google Gemini 2.5 Flash + OpenAI
- **TTS**: Azure Cognitive Services
- **Search**: FAISS + Sentence Transformers

## 📁 Project Structure

```
Adobe_Round3/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── semantic.py      # Search & indexing
│   │   ├── llm_adapter.py   # AI integration
│   │   ├── tts_adapter.py   # Text-to-speech
│   │   └── indexer.py       # File management
│   ├── requirements.txt
│   └── data/                # Uploaded PDFs
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   └── App.js          # Main app
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
- AI-powered document analysis
- Cross-document insights generation
- Podcast creation from text
- Professional UI/UX design

Happy coding! 🚀
