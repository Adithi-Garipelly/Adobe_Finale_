import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAPI } from './APIContext';

const FileContext = createContext();

export const useFileContext = () => {
  const context = useContext(FileContext);
  if (!context) {
    throw new Error('useFileContext must be used within a FileProvider');
  }
  return context;
};

export const FileProvider = ({ children }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const { getDocuments, deleteDocument } = useAPI();

  // Load existing documents on mount
  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const response = await getDocuments();
        if (response.documents) {
          setUploadedFiles(response.documents);
        }
      } catch (error) {
        console.error('Error loading documents:', error);
      }
    };

    loadDocuments();
  }, [getDocuments]);

  const handleFileUpload = async (file) => {
    try {
      // For now, create a mock file object
      // In a real implementation, this would call the API
      const mockFile = {
        id: Date.now().toString(),
        filename: file.name,
        file_size: file.size,
        uploaded_at: new Date().toISOString()
      };
      
      setUploadedFiles(prev => [...prev, mockFile]);
      return mockFile;
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  };

  const handleFileRemove = async (fileId) => {
    try {
      await deleteDocument(fileId);
      setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
      
      // If the removed file was selected, clear selection
      if (selectedFile && selectedFile.id === fileId) {
        setSelectedFile(null);
      }
    } catch (error) {
      console.error('Error removing file:', error);
      throw error;
    }
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
  };

  const value = {
    uploadedFiles,
    selectedFile,
    handleFileUpload,
    handleFileRemove,
    handleFileSelect,
  };

  return (
    <FileContext.Provider value={value}>
      {children}
    </FileContext.Provider>
  );
};
