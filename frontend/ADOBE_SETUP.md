# Adobe PDF Embed API Setup

## 🎯 **Why Adobe PDF Embed API?**

- ✅ **Professional PDF viewing** with advanced features
- ✅ **Reliable text selection** for insights generation
- ✅ **Cross-browser compatibility** 
- ✅ **Production-ready** (unlike iframe which has limitations)
- ✅ **Advanced controls** (zoom, search, bookmarks, thumbnails)

## 🔑 **Get Your Free API Key**

1. **Visit**: https://www.adobe.com/go/dcsdks_credentials
2. **Sign in** with Adobe account (free)
3. **Create new credentials** for "PDF Embed API"
4. **Copy your Client ID**

## ⚙️ **Setup Steps**

### **1. Create Environment File**
Create `frontend/.env` file:
```bash
# Adobe PDF Embed API Key
REACT_APP_ADOBE_EMBED_API_KEY=your-actual-client-id-here

# Backend API URL
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_BACKEND_URL=http://localhost:8000
```

### **2. Replace Placeholder**
Replace `your-actual-client-id-here` with your real Adobe Client ID

### **3. Restart Frontend**
```bash
cd frontend
npm start
```

## 🎉 **Features You'll Get**

- **Professional PDF viewer** with Adobe branding
- **Text selection** that triggers insights generation
- **Zoom controls** and page navigation
- **Search functionality** within PDFs
- **Thumbnail view** for easy navigation
- **Bookmarks** support
- **Full-screen mode**
- **Mobile responsive** design

## 🚀 **Production Ready**

This implementation will work reliably in:
- ✅ **Local development**
- ✅ **Staging environments**
- ✅ **Production deployments**
- ✅ **All modern browsers**
- ✅ **Mobile devices**

## 📝 **Text Selection Events**

The viewer automatically captures text selection and triggers:
- `SELECTION_END` event when user selects text
- Automatic insights generation
- Podcast script creation from selected content

**Your system is now competition-ready with professional PDF viewing!** 🏆
