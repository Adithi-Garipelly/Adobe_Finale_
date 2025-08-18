import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const PDFContainer = styled.div`
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const PDFFrame = styled.iframe`
  width: 100%;
  height: 100%;
  border: none;
`;

const ManualInputPanel = styled.div`
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 15px;
  margin-top: 15px;
`;

const ManualInput = styled.textarea`
  width: 100%;
  min-height: 100px;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 10px;
`;

const GenerateButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s ease;
  
  &:hover {
    background: #5a6fd8;
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const PDFViewer = ({ selectedFile, onTextSelection }) => {
  const [manualText, setManualText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    // Global event listeners for text selection
    const handleTextSelection = () => {
      const selection = window.getSelection();
      if (selection && selection.toString().trim()) {
        const selectedText = selection.toString().trim();
        if (selectedText.length > 10) { // Only process meaningful selections
          onTextSelection(selectedText);
        }
      }
    };

    // Add event listeners
    document.addEventListener('mouseup', handleTextSelection);
    document.addEventListener('keyup', handleTextSelection);
    document.addEventListener('selectionchange', handleTextSelection);

    return () => {
      // Cleanup event listeners
      document.removeEventListener('mouseup', handleTextSelection);
      document.removeEventListener('keyup', handleTextSelection);
      document.removeEventListener('selectionchange', handleTextSelection);
    };
  }, [onTextSelection]);

  const handleManualTextSubmit = async () => {
    if (!manualText.trim()) return;
    
    setIsGenerating(true);
    try {
      await onTextSelection(manualText.trim());
    } catch (error) {
      console.error('Error processing manual text:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  if (!selectedFile) {
    return (
      <PDFContainer>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100%',
          color: '#666',
          fontSize: '16px'
        }}>
          No PDF loaded. Upload a PDF file to get started.
        </div>
      </PDFContainer>
    );
  }

  const pdfUrl = selectedFile.startsWith('http') 
    ? selectedFile 
    : `/api/files/${encodeURIComponent(selectedFile)}`;

  return (
    <PDFContainer>
      <PDFFrame
        src={`https://mozilla.github.io/pdf.js/web/viewer.html?file=${encodeURIComponent(pdfUrl)}`}
        title="PDF Viewer"
      />
      
      <ManualInputPanel>
        <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#495057' }}>
          Manual Text Input (for testing)
        </h4>
        <ManualInput
          placeholder="Paste or type text here to test insights generation..."
          value={manualText}
          onChange={(e) => setManualText(e.target.value)}
        />
        <GenerateButton
          onClick={handleManualTextSubmit}
          disabled={!manualText.trim() || isGenerating}
        >
          {isGenerating ? 'Generating...' : 'Generate Insights'}
        </GenerateButton>
      </ManualInputPanel>
    </PDFContainer>
  );
};

export default PDFViewer;
