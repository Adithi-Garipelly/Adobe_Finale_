import React, { useCallback, useState } from 'react';
import styled from 'styled-components';

const PageContainer = styled.div`
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
`;

const PageTitle = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 16px 0;
`;

const PageSubtitle = styled.p`
  font-size: 18px;
  color: #666;
  margin: 0 0 40px 0;
  line-height: 1.5;
`;

const UploadArea = styled.div`
  border: 3px dashed #667eea;
  border-radius: 16px;
  padding: 60px 40px;
  background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%);
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 30px;
  
  &:hover {
    border-color: #5a67d8;
    background: linear-gradient(135deg, #f0f4ff 0%, #e0f0ff 100%);
    transform: translateY(-2px);
  }
`;

const UploadIcon = styled.div`
  font-size: 80px;
  margin-bottom: 24px;
  opacity: 0.8;
`;

const UploadText = styled.div`
  font-size: 20px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 12px;
`;

const UploadSubtext = styled.div`
  font-size: 16px;
  color: #666;
  margin-bottom: 8px;
`;

const FileInput = styled.input`
  display: none;
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
  margin-top: 20px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const FileList = styled.div`
  margin-top: 30px;
  text-align: left;
`;

const FileItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e9ecef;
    border-color: #667eea;
  }
`;

const FileInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const FileIcon = styled.div`
  font-size: 24px;
  color: #667eea;
`;

const FileDetails = styled.div``;

const FileName = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
`;

const FileSize = styled.div`
  font-size: 14px;
  color: #666;
`;

const FileActions = styled.div`
  display: flex;
  gap: 8px;
`;

const ActionButton = styled.button`
  background: ${props => props.primary ? '#667eea' : '#6c757d'};
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  
  &:hover {
    background: ${props => props.primary ? '#5a67d8' : '#5a6268'};
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const RemoveButton = styled.button`
  background: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
  
  &:hover {
    background: #c82333;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: #666;
`;

const EmptyIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
`;

const EmptyTitle = styled.h3`
  font-size: 20px;
  font-weight: 500;
  margin: 0 0 16px 0;
  color: #333;
`;

const EmptyText = styled.p`
  font-size: 16px;
  margin: 0;
  color: #888;
`;

function UploadPage({ onFileSelect, uploadedFiles = [], onFileRemove, onOpenPDF }) {
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = useCallback((event) => {
    console.log('🔍 handleFileChange called');
    console.log('🔍 event.target.files:', event.target.files);
    
    const files = Array.from(event.target.files);
    console.log('🔍 Converted to array:', files);
    
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    console.log('🔍 Filtered PDF files:', pdfFiles);
    
    if (pdfFiles.length === 0) {
      alert('Please select PDF files only.');
      return;
    }
    
    console.log('🔍 Calling onFileSelect with:', pdfFiles);
    // Pass all PDF files as an array to parent
    onFileSelect(pdfFiles);
  }, [onFileSelect]);

  const handleUploadClick = () => {
    document.getElementById('file-input').click();
  };

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setDragActive(true);
    }
  }, []);

  const handleDragOut = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    console.log('🔍 handleDrop called');
    console.log('🔍 e.dataTransfer.files:', e.dataTransfer.files);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const files = Array.from(e.dataTransfer.files);
      console.log('🔍 Converted to array:', files);
      
      const pdfFiles = files.filter(file => file.type === 'application/pdf');
      console.log('🔍 Filtered PDF files:', pdfFiles);
      
      if (pdfFiles.length === 0) {
        alert('Please drop PDF files only.');
        return;
      }
      
      console.log('🔍 Calling onFileSelect with:', pdfFiles);
      // Pass all PDF files as an array to parent
      onFileSelect(pdfFiles);
    }
  }, [onFileSelect]);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <PageContainer>
      <PageTitle>Upload PDFs</PageTitle>
      <PageSubtitle>
        Upload up to 30 PDF files for intelligent analysis
      </PageSubtitle>
      
      <UploadArea 
        onClick={handleUploadClick}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        style={{
          borderColor: dragActive ? '#5a67d8' : '#667eea',
          background: dragActive 
            ? 'linear-gradient(135deg, #f0f4ff 0%, #e0f0ff 100%)'
            : 'linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%)'
        }}
      >
        <UploadIcon>⬆️</UploadIcon>
        <UploadText>
          {dragActive ? 'Drop PDFs here!' : 'Drag & drop PDFs here, or click to select'}
        </UploadText>
        <UploadSubtext>Supports up to 30 PDF files • Maximum 50MB per file</UploadSubtext>
      </UploadArea>
      
      <UploadButton onClick={handleUploadClick}>
        Choose PDF Files
      </UploadButton>
      
      <FileInput
        id="file-input"
        type="file"
        accept=".pdf"
        multiple
        onChange={handleFileChange}
      />
      
      {/* File List */}
      {uploadedFiles.length > 0 ? (
        <FileList>
          <h3 style={{ marginBottom: '20px', color: '#333', textAlign: 'center' }}>
            📚 Uploaded Files ({uploadedFiles.length})
          </h3>
          {uploadedFiles.map((file) => (
            <FileItem key={file.id}>
              <FileInfo>
                <FileIcon>📄</FileIcon>
                <FileDetails>
                  <FileName>{file.name}</FileName>
                  <FileSize>
                    {formatFileSize(file.size)} • Uploaded {file.uploaded.toLocaleDateString()}
                  </FileSize>
                </FileDetails>
              </FileInfo>
              <FileActions>
                <ActionButton 
                  primary
                  onClick={() => onOpenPDF(file)}
                >
                  View
                </ActionButton>
                <RemoveButton onClick={() => onFileRemove(file.id)}>
                  Remove
                </RemoveButton>
              </FileActions>
            </FileItem>
          ))}
        </FileList>
      ) : (
        <EmptyState>
          <EmptyIcon>📄</EmptyIcon>
          <EmptyTitle>No PDFs Uploaded Yet</EmptyTitle>
          <EmptyText>
            Upload your first PDF to get started with AI-powered analysis
          </EmptyText>
        </EmptyState>
      )}
    </PageContainer>
  );
}

export default UploadPage;
