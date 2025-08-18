import React, { useState } from 'react';
import styled from 'styled-components';
import Header from './components/Header';
import UploadPage from './components/UploadPage';
import PDFViewerPage from './components/PDFViewerPage';
import InsightsPage from './components/InsightsPage';
import PodcastPage from './components/PodcastPage';

const AppContainer = styled.div`
  min-height: 100vh;
  background: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
`;

const MainContent = styled.div`
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
`;

const TabContainer = styled.div`
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
`;

const Tab = styled.button`
  flex: 1;
  padding: 16px 24px;
  border: none;
  background: ${props => props.active ? '#667eea' : 'transparent'};
  color: ${props => props.active ? 'white' : '#666'};
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
  
  &:hover {
    background: ${props => props.active ? '#667eea' : '#f0f0f0'};
  }
`;

const TabIcon = styled.span`
  margin-right: 8px;
  font-size: 16px;
`;

function App() {
  const [currentView, setCurrentView] = useState('upload');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedText, setSelectedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [podcastData, setPodcastData] = useState(null);

  // Upload file to backend
  const uploadFileToBackend = async (file) => {
    try {
      const formData = new FormData();
      formData.append('files', file);
      
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log('✅ File uploaded successfully:', result);
      return result;
    } catch (error) {
      console.error('❌ Upload failed:', error);
      throw error;
    }
  };

  const handleFileSelect = async (files) => {
    if (!files || files.length === 0) return;
    
    try {
      setIsLoading(true);
      
      const uploadPromises = files.map(async (file) => {
        console.log('📤 Uploading file to backend:', file.name);
        const uploadResult = await uploadFileToBackend(file);
        
        return {
          id: Date.now() + Math.random(),
          name: file.name,
          file: file,
          size: file.size,
          uploaded: new Date(),
          backendPath: uploadResult.uploaded[0] || file.name
        };
      });
      
      const newFiles = await Promise.all(uploadPromises);
      setUploadedFiles(prev => [...prev, ...newFiles]);
      console.log('✅ Files uploaded successfully:', newFiles);
      
    } catch (error) {
      console.error('❌ File selection failed:', error);
      alert(`Failed to upload files: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileRemove = async (fileId) => {
    try {
      const fileToRemove = uploadedFiles.find(f => f.id === fileId);
      if (!fileToRemove) return;
      
      // Remove from backend if it exists there
      if (fileToRemove.backendPath) {
        try {
          const response = await fetch(`http://localhost:8000/documents/${fileToRemove.backendPath}`, {
            method: 'DELETE',
          });
          if (response.ok) {
            console.log('✅ File removed from backend:', fileToRemove.backendPath);
          }
        } catch (error) {
          console.warn('⚠️ Failed to remove from backend:', error);
        }
      }
      
      // Remove from frontend state
      setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
      
      // If the removed file was selected, clear selection
      if (selectedFile && selectedFile.id === fileId) {
        setSelectedFile(null);
        setCurrentView('upload');
      }
      
      console.log('✅ File removed successfully');
    } catch (error) {
      console.error('❌ File removal failed:', error);
      alert('Failed to remove file');
    }
  };

  const handleOpenPDF = (file) => {
    setSelectedFile(file);
    setCurrentView('viewer');
    setSelectedText('');
  };

  const handleTextSelection = (text) => {
    setSelectedText(text);
    setCurrentView('insights');
  };

  const handleGeneratePodcast = async () => {
    if (!selectedText) {
      alert('Please select text first');
      return;
    }
    
    try {
      setIsLoading(true);
      
      const response = await fetch('http://localhost:8000/podcast/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: selectedText,
          filename: `podcast_${Date.now()}.mp3`
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Podcast generation failed: ${response.statusText}`);
      }
      
      const result = await response.json();
      setPodcastData(result);
      setCurrentView('podcast');
      console.log('✅ Podcast generated successfully:', result);
    } catch (error) {
      console.error('❌ Podcast generation failed:', error);
      alert('Failed to generate podcast');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    if (currentView === 'viewer') {
      setCurrentView('upload');
      setSelectedFile(null);
    } else if (currentView === 'insights') {
      setCurrentView('viewer');
    } else if (currentView === 'podcast') {
      setCurrentView('insights');
    }
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'upload':
        return (
          <UploadPage
            onFileSelect={handleFileSelect}
            uploadedFiles={uploadedFiles}
            onFileRemove={handleFileRemove}
            onOpenPDF={handleOpenPDF}
          />
        );
      case 'viewer':
        return (
          <PDFViewerPage
            file={selectedFile}
            isLoading={isLoading}
            onTextSelection={handleTextSelection}
            onBack={handleBack}
            uploadedFiles={uploadedFiles}
            onFileSelect={handleOpenPDF}
          />
        );
      case 'insights':
        return (
          <InsightsPage
            selectedText={selectedText}
            selectedFile={selectedFile}
            onGeneratePodcast={handleGeneratePodcast}
            onBack={handleBack}
          />
        );
      case 'podcast':
        return (
          <PodcastPage
            podcastData={podcastData}
            onBack={handleBack}
            onBackToViewer={() => setCurrentView('viewer')}
          />
        );
      default:
        return (
          <UploadPage
            onFileSelect={handleFileSelect}
            uploadedFiles={uploadedFiles}
            onFileRemove={handleFileRemove}
            onOpenPDF={handleOpenPDF}
          />
        );
    }
  };

  return (
    <AppContainer>
      <Header onUpload={() => setCurrentView('upload')} />
      <MainContent>
        <TabContainer>
          <Tab 
            active={currentView === 'upload'} 
            onClick={() => setCurrentView('upload')}
          >
            <TabIcon>📤</TabIcon>
            Upload PDFs
          </Tab>
          <Tab 
            active={currentView === 'viewer'} 
            onClick={() => setCurrentView('viewer')}
          >
            <TabIcon>📄</TabIcon>
            PDF Viewer
          </Tab>
          <Tab 
            active={currentView === 'insights'} 
            onClick={() => setCurrentView('insights')}
          >
            <TabIcon>🧠</TabIcon>
            AI Insights
          </Tab>
          <Tab 
            active={currentView === 'podcast'} 
            onClick={() => setCurrentView('podcast')}
          >
            <TabIcon>🎙️</TabIcon>
            Podcast
          </Tab>
        </TabContainer>
        
        {renderCurrentView()}
      </MainContent>
    </AppContainer>
  );
}

export default App;
