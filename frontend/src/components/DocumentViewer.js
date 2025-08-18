import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const ViewerContainer = styled.div`
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
`;

const ViewerHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background: #fafafa;
`;

const ViewerTitle = styled.h2`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
`;

const ViewerContent = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
`;

const LoadingSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
`;

const Spinner = styled.div`
  width: 60px;
  height: 60px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingText = styled.p`
  color: #666;
  font-size: 16px;
  margin: 0;
`;

const PDFViewer = styled.div`
  width: 100%;
  height: 100%;
  border: none;
`;

const NoFileMessage = styled.div`
  text-align: center;
  color: #666;
`;

const NoFileIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
`;

const NoFileTitle = styled.h3`
  font-size: 20px;
  font-weight: 500;
  margin: 0 0 10px 0;
  color: #333;
`;

const NoFileText = styled.p`
  font-size: 14px;
  margin: 0;
  color: #888;
`;

function DocumentViewer({ file, isLoading, onTextSelection }) {
  const [viewerReady, setViewerReady] = useState(false);

  useEffect(() => {
    if (file) {
      // Simulate PDF viewer loading
      const timer = setTimeout(() => {
        setViewerReady(true);
      }, 2000);
      
      return () => clearTimeout(timer);
    } else {
      setViewerReady(false);
    }
  }, [file]);

  if (!file) {
    return (
      <ViewerContainer>
        <ViewerHeader>
          <ViewerTitle>Document Viewer</ViewerTitle>
        </ViewerHeader>
        <ViewerContent>
          <NoFileMessage>
            <NoFileIcon>📄</NoFileIcon>
            <NoFileTitle>No Document Loaded</NoFileTitle>
            <NoFileText>Upload a PDF to get started</NoFileText>
          </NoFileMessage>
        </ViewerContent>
      </ViewerContainer>
    );
  }

  if (isLoading || !viewerReady) {
    return (
      <ViewerContainer>
        <ViewerHeader>
          <ViewerTitle>Loading Document: {file.name}</ViewerTitle>
        </ViewerHeader>
        <ViewerContent>
          <LoadingSpinner>
            <Spinner />
            <LoadingText>Loading document...</LoadingText>
          </LoadingSpinner>
        </ViewerContent>
      </ViewerContainer>
    );
  }

  return (
    <ViewerContainer>
      <ViewerHeader>
        <ViewerTitle>📄 {file.name}</ViewerTitle>
      </ViewerHeader>
      <ViewerContent>
        <PDFViewer>
          {/* For now, show a placeholder. In production, this would be the Adobe PDF Embed API */}
          <div style={{ 
            width: '100%', 
            height: '100%', 
            background: '#f8f9fa',
            border: '2px dashed #dee2e6',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#6c757d',
            fontSize: '16px'
          }}>
            PDF Viewer Placeholder
            <br />
            <small>Adobe PDF Embed API would be integrated here</small>
          </div>
        </PDFViewer>
      </ViewerContent>
    </ViewerContainer>
  );
}

export default DocumentViewer;
