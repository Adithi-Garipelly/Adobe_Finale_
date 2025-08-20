# 🎯 Adobe Finale - Judge Setup Guide

**Complete Setup Instructions for Hackathon Judges**  
*This guide ensures judges can run your project without any issues*

---

## 🚨 IMPORTANT: Before Starting

### System Requirements
- **Operating System**: macOS 10.15+ or Windows 10+
- **Python**: 3.10.13 (exact version recommended)
- **Node.js**: 16.0.0 or higher
- **RAM**: Minimum 4GB, recommended 8GB
- **Storage**: At least 2GB free space

### Port Requirements
- **Port 8080**: Backend API (must be free)
- **Port 3000**: Frontend (must be free)

---

## 🚀 Step-by-Step Setup (Mac)

### Step 1: Verify Prerequisites
```bash
# Check Python version (must be 3.10+)
python3 --version

# Check Node.js version (must be 16+)
node --version

# Check npm version
npm --version
```

### Step 2: Clone/Download Project
```bash
# Navigate to your download location
cd ~/Downloads  # or wherever you downloaded the project

# If it's a zip file, extract it first
unzip Adobe_Round3.zip

# Navigate into the project folder
cd Adobe_Round3
```

### Step 3: Start Backend (Terminal 1)
```bash
# Open Terminal 1
# Navigate to backend folder
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# You should see (.venv) at the start of your prompt

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

**Expected Output:**
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

### Step 4: Start Frontend (Terminal 2)
```bash
# Open Terminal 2 (new terminal window)
# Navigate to frontend folder
cd frontend

# Install Node.js dependencies
npm install

# Start the frontend
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view adobe-finale in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

### Step 5: Verify Everything is Working
1. **Backend Check**: Open http://localhost:8080/health in browser
   - Should show: `{"status":"ok","pdf_count":X}`
2. **Frontend Check**: Open http://localhost:3000 in browser
   - Should show the Adobe Finale application

---

## 🚀 Step-by-Step Setup (Windows)

### Step 1: Verify Prerequisites
```cmd
# Check Python version (must be 3.10+)
python --version

# Check Node.js version (must be 16+)
node --version

# Check npm version
npm --version
```

### Step 2: Clone/Download Project
```cmd
# Navigate to your download location
cd C:\Users\YourUsername\Downloads

# If it's a zip file, extract it first (right-click → Extract All)
# Navigate into the project folder
cd Adobe_Round3
```

### Step 3: Start Backend (Command Prompt 1)
```cmd
# Open Command Prompt 1
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# You should see (.venv) at the start of your prompt

# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

**Expected Output:**
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

### Step 4: Start Frontend (Command Prompt 2)
```cmd
# Open Command Prompt 2 (new command prompt window)
# Navigate to frontend folder
cd frontend

# Install Node.js dependencies
npm install

# Start the frontend
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view adobe-finale in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

### Step 5: Verify Everything is Working
1. **Backend Check**: Open http://localhost:8080/health in browser
   - Should show: `{"status":"ok","pdf_count":X}`
2. **Frontend Check**: Open http://localhost:3000 in browser
   - Should show the Adobe Finale application

---

## 🔧 Troubleshooting Guide

### Issue 1: Port Already in Use

#### Mac/Linux
```bash
# Check what's using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>

# Check what's using port 3000
lsof -i :3000

# Kill the process
kill -9 <PID>
```

#### Windows
```cmd
# Check what's using port 8080
netstat -an | findstr :8080

# Kill the process
taskkill /PID <PID> /F

# Check what's using port 3000
netstat -an | findstr :3000

# Kill the process
taskkill /PID <PID> /F
```

### Issue 2: Python Module Not Found
```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Set Python path
export PYTHONPATH=$PWD     # Mac/Linux
set PYTHONPATH=%CD%        # Windows
```

### Issue 3: npm Install Fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Issue 4: Backend Won't Start
```bash
# Check if you're in the right directory
pwd  # Should show .../Adobe_Round3/backend

# Check if virtual environment is activated
which python  # Should show .../.venv/bin/python

# Check Python version
python --version  # Should be 3.10+
```

---

## 🎯 Demo Instructions for Judges

### 1. **Upload Test Documents**
- Go to http://localhost:3000
- Click "Upload Files" button
- Select 2-3 PDF research papers (any academic papers work)
- Wait for green checkmark (indexing complete)

### 2. **Generate Insights**
- Click on any uploaded PDF to open it
- Select text by highlighting with mouse
- Click "Generate Insights" button
- Wait for AI analysis (5-10 seconds)
- View the generated insights

### 3. **Create Podcast**
- After insights are generated
- Click "Generate Podcast" button
- Wait for audio generation (10-30 seconds)
- Play the generated podcast audio
- Verify it's a natural conversation (Sarah & Alex)

### 4. **Test Additional Features**
- Try different text selections
- Generate multiple podcasts
- Test file uploads with different PDFs
- Explore the interface navigation

---

## 📊 What to Look For

### ✅ **Working Features**
- PDF uploads complete successfully
- Text selection works in PDF viewer
- AI insights generation completes
- Podcast audio plays properly
- Natural conversation format (no stage directions)
- Multiple voices in podcast (Sarah & Alex)

### ❌ **Common Issues to Check**
- Backend starts without errors
- Frontend loads completely
- No console errors in browser
- Audio files are generated (not empty)
- Ports 8080 and 3000 are accessible

---

## 🆘 Emergency Contacts

If you encounter issues that aren't covered in this guide:

1. **Check the main README.md** for additional troubleshooting
2. **Look at terminal output** for error messages
3. **Check browser console** (F12) for frontend errors
4. **Verify all prerequisites** are installed correctly

---

## 🎉 Ready to Judge!

Your Adobe Finale application is now ready for evaluation. The system demonstrates:

✅ **Complete AI Integration** (Gemini 2.5 Flash)  
✅ **Professional TTS** (Azure Cognitive Services)  
✅ **Natural Podcast Generation** (Sarah & Alex hosts)  
✅ **Cross-Document Analysis** (Semantic search)  
✅ **Modern Web Interface** (React + FastAPI)  
✅ **Hackathon-Ready** (No setup issues for judges)  

**Good luck with your submission! 🚀**
