import React, { useCallback } from 'react';
import styled from 'styled-components';

const UploadContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
`;

const UploadIcon = styled.div`
  font-size: 80px;
  margin-bottom: 24px;
  opacity: 0.7;
`;

const UploadTitle = styled.h2`
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
`;

const UploadDescription = styled.p`
  font-size: 16px;
  color: #666;
  margin: 0 0 32px 0;
  max-width: 500px;
  line-height: 1.5;
`;

const UploadButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const FileInput = styled.input`
  display: none;
`;

const SupportedFormats = styled.div`
  margin-top: 24px;
  font-size: 14px;
  color: #888;
`;

function FileUpload({ onFileSelect }) {
  const handleFileChange = useCallback((event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      onFileSelect(file);
    } else if (file) {
      alert('Please select a PDF file.');
    }
  }, [onFileSelect]);

  const handleUploadClick = () => {
    document.getElementById('file-input').click();
  };

  return (
    <UploadContainer>
      <UploadIcon>📄</UploadIcon>
      <UploadTitle>Upload Your PDF</UploadTitle>
      <UploadDescription>
        Get AI-powered insights, semantic search, and generate podcasts from your documents. 
        Simply upload a PDF and start exploring the connections.
      </UploadDescription>
      
      <UploadButton onClick={handleUploadClick}>
        Choose PDF File
      </UploadButton>
      
      <FileInput
        id="file-input"
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
      />
      
      <SupportedFormats>
        Supported format: PDF only
      </SupportedFormats>
    </UploadContainer>
  );
}

export default FileUpload;
