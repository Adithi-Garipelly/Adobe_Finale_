#!/bin/bash

# Adobe Finale - GitHub Repository Setup Script
# This script automates the GitHub repository setup process

echo "🚀 Setting up GitHub repository for Adobe Finale..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -f "Dockerfile" ]; then
    echo "❌ Please run this script from the project root directory (Adobe_Round3)"
    exit 1
fi

# Initialize git repository
echo "📁 Initializing git repository..."
git init

# Add all files
echo "📝 Adding all files to git..."
git add .

# Initial commit
echo "💾 Making initial commit..."
git commit -m "Initial commit: Adobe Finale - Document Insight & Engagement System

- AI-Powered Research Analysis with Natural Language Podcast Generation
- FastAPI Backend with Google Gemini 2.5 Flash
- React Frontend with Azure TTS Integration
- Docker containerization for easy deployment
- Comprehensive documentation and setup guides"

echo ""
echo "✅ Git repository initialized successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://github.com/new"
echo "2. Repository name: adobe-finale-hackathon"
echo "3. Description: AI-Powered Research Analysis with Natural Language Podcast Generation"
echo "4. Make it Public"
echo "5. Don't initialize with README (we already have one)"
echo "6. Click 'Create repository'"
echo ""
echo "🔗 After creating the repository, run these commands:"
echo "git remote add origin https://github.com/YOUR_USERNAME/adobe-finale-hackathon.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "🎉 Your Adobe Finale project will be live on GitHub!"
