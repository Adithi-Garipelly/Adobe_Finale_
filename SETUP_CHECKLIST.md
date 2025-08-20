# ✅ Adobe Finale - Setup Checklist for Judges

**Follow this checklist to get your Adobe Finale application running in 5 minutes**

---

## 🚨 Prerequisites Check

- [ ] **Python 3.10+** installed (`python --version`)
- [ ] **Node.js 16+** installed (`node --version`)
- [ ] **npm** installed (`npm --version`)
- [ ] **Ports 8080 & 3000** are free
- [ ] **2GB free disk space** available

---

## 🚀 Quick Setup (Choose One)

### Option A: Automated Script (Recommended)
- [ ] **Mac/Linux**: Run `./QUICK_START.sh`
- [ ] **Windows**: Run `QUICK_START.bat`
- [ ] Wait for "Adobe Finale is now running!" message

### Option B: Manual Setup
- [ ] **Backend**: Follow steps in `JUDGE_SETUP_GUIDE.md`
- [ ] **Frontend**: Follow steps in `JUDGE_SETUP_GUIDE.md`

---

## ✅ Verification Steps

- [ ] **Backend Health**: http://localhost:8080/health shows `{"status":"ok"}`
- [ ] **Frontend Loads**: http://localhost:3000 shows Adobe Finale app
- [ ] **No Console Errors**: Browser console (F12) is clean
- [ ] **Ports Active**: 8080 and 3000 are listening

---

## 🎯 Demo Flow

- [ ] **Upload PDFs**: Drag & drop 2-3 research papers
- [ ] **Wait for Indexing**: Green checkmarks appear
- [ ] **Open PDF**: Click any uploaded file
- [ ] **Select Text**: Highlight text with mouse
- [ ] **Generate Insights**: Click "Generate Insights" button
- [ ] **Create Podcast**: Click "Generate Podcast" button
- [ ] **Play Audio**: Verify podcast plays with natural voices

---

## 🔧 If Something Goes Wrong

- [ ] **Check Logs**: Look at terminal output
- [ ] **Verify Ports**: Ensure 8080 and 3000 are free
- [ ] **Restart Services**: Kill processes and restart
- [ ] **Check Dependencies**: Verify Python/Node versions
- [ ] **Review README**: Check main README.md for help

---

## 📞 Emergency Contacts

- **Main README**: `README.md`
- **Detailed Guide**: `JUDGE_SETUP_GUIDE.md`
- **Project Summary**: `PROJECT_SUMMARY.md`
- **Troubleshooting**: See troubleshooting section in guides

---

## 🎉 Success Indicators

✅ **Backend**: Running on port 8080 with health check passing  
✅ **Frontend**: Loads completely on port 3000  
✅ **PDF Upload**: Files upload and index successfully  
✅ **AI Analysis**: Insights generate in 5-10 seconds  
✅ **Podcast Generation**: Audio files created and play properly  
✅ **Natural Voices**: Sarah & Alex hosts sound natural  

---

## 🚀 Ready to Judge!

**Your Adobe Finale application is now ready for evaluation!**

**Frontend**: http://localhost:3000  
**Backend**: http://localhost:8080  
**API Docs**: http://localhost:8080/docs  

**Good luck with your submission! 🎯**
