import React, { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import styled from 'styled-components';

const PageContainer = styled.div`
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
`;

const PDFViewerSection = styled.div`
  flex: 2;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const ViewerHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const ViewerTitle = styled.h2`
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ViewerControls = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const ControlButton = styled.button`
  background: white;
  border: 1px solid #e0e0e0;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  
  &:hover {
    background: #f8f9fa;
    border-color: #667eea;
  }
`;

const PDFContainer = styled.div`
  flex: 1;
  position: relative;
  background: #f8f9fa;
`;

const AdobeViewerContainer = styled.div`
  width: 100%;
  height: 100%;
  background: white;
`;

const LoadingSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 20px;
  color: #666;
`;

const Spinner = styled.div`
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  color: #c33;
  max-width: 400px;
`;

const SidebarSection = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const SidebarPanel = styled.div`
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
`;

const PanelHeader = styled.h3`
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const PanelContent = styled.div`
  color: #666;
  font-size: 14px;
  line-height: 1.5;
`;

const TextInput = styled.textarea`
  width: 100%;
  min-height: 120px;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  font-family: inherit;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const GenerateButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 12px;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const PDFListPanel = styled.div`
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
`;

const PDFListItem = styled.div`
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: ${props => props.active ? '#e3f2fd' : '#fafafa'};
  border-color: ${props => props.active ? '#2196f3' : '#e0e0e0'};
  
  &:hover {
    background: ${props => props.active ? '#e3f2fd' : '#f0f0f0'};
    border-color: #2196f3;
  }
`;

const PDFFileName = styled.div`
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
`;

const PDFFileInfo = styled.div`
  font-size: 12px;
  color: #666;
`;

function PDFViewerPage({ file, isLoading: externalLoading, onTextSelection, onBack, uploadedFiles = [], onFileSelect }) {
  const [currentFile, setCurrentFile] = useState(file);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [manualText, setManualText] = useState('');
  const adobeViewerRef = useRef(null);
  const adobeViewerInstanceRef = useRef(null);
  
  // Generate a stable ID for the Adobe viewer container
  const viewerContainerId = useMemo(() => `adobe-dc-view-${Math.random().toString(36).substr(2, 9)}`, []);

  // Adobe PDF Embed API configuration
  const adobeConfig = useMemo(() => {
    const clientId = process.env.REACT_APP_ADOBE_EMBED_API_KEY || 'your-adobe-client-id';
    console.log('🔑 Adobe API Key:', clientId);
    
    return {
      clientId,
      defaultViewMode: 'FIT_WIDTH',
      showDownloadPDF: false,
      showPrintPDF: false,
      showFullScreen: true,
      showLeftHandPanel: true,
      showAnnotationTools: false,
      enableFormFilling: false,
      showBookmarks: true,
      showThumbnails: true,
      showPageControls: true,
      showZoomControl: true,
      showSearch: true,
      showSecondaryToolbar: false,
      showToolbarControl: true
    };
  }, []);

  // Initialize Adobe viewer
  const initializeAdobeViewer = useCallback(() => {
    try {
      console.log('🔧 Initializing Adobe viewer...');
      
      // Check if client ID is valid
      if (!adobeConfig.clientId || adobeConfig.clientId === 'your-adobe-client-id') {
        console.error('❌ Invalid Adobe client ID:', adobeConfig.clientId);
        setError('Adobe API key not configured. Please check your .env file.');
        setIsLoading(false);
        return;
      }
      
      // Wait for container to be available
      const container = document.getElementById(viewerContainerId);
      if (!container) {
        console.log('⏳ Container not ready yet, retrying in 100ms...');
        setTimeout(() => initializeAdobeViewer(), 100);
        return;
      }
      
      if (window.AdobeDC && window.AdobeDC.View && container) {
        console.log('✅ All prerequisites met, configuring Adobe viewer...');
        
        // Clear any existing content
        container.innerHTML = '';
        
        // Configure Adobe viewer
        window.AdobeDC.View.configure(adobeConfig);
        console.log('✅ Adobe viewer configured');
        
        // Create Adobe viewer instance
        const adobeDCView = new window.AdobeDC.View({
          clientId: adobeConfig.clientId,
          divId: viewerContainerId,
        });
        console.log('✅ Adobe viewer instance created:', adobeDCView);

        // Register callbacks
        adobeDCView.registerCallback(
          window.AdobeDC.View.Enum.CoreControls.API_EVENT_TYPE.SELECTION_END,
          (event) => {
            console.log('📝 Text selected:', event);
            if (event.data && event.data.text) {
              onTextSelection(event.data.text);
            }
          }
        );

        adobeDCView.registerCallback(
          window.AdobeDC.View.Enum.CoreControls.API_EVENT_TYPE.VIEWER_READY,
          () => {
            console.log('✅ Adobe viewer ready');
            setIsLoading(false);
            setError(null);
          }
        );

        adobeDCView.registerCallback(
          window.AdobeDC.View.Enum.CoreControls.API_EVENT_TYPE.ERROR,
          (error) => {
            console.error('❌ Adobe viewer error:', error);
            setError('PDF viewer error. Please try again.');
            setIsLoading(false);
          }
        );

        adobeViewerInstanceRef.current = adobeDCView;
        console.log('✅ Adobe viewer initialization complete');
      } else {
        console.error('❌ Prerequisites not met for Adobe viewer initialization');
        
        // Retry initialization if AdobeDC is not ready yet
        if (!window.AdobeDC || !window.AdobeDC.View) {
          console.log('⏳ AdobeDC not ready yet, retrying in 200ms...');
          setTimeout(() => initializeAdobeViewer(), 200);
          return;
        }
        
        setError('Failed to initialize PDF viewer - missing prerequisites');
      }
    } catch (error) {
      console.error('❌ Error initializing Adobe viewer:', error);
      setError('Failed to initialize PDF viewer');
      setIsLoading(false);
    }
  }, [adobeConfig, onTextSelection, viewerContainerId]);

  // Load Adobe PDF Embed API script
  useEffect(() => {
    if (!window.AdobeDC) {
      console.log('📜 Loading Adobe PDF Embed API script...');
      const script = document.createElement('script');
      script.src = 'https://documentcloud.adobe.com/view-sdk/main.js';
      script.async = true;
      script.defer = true;
      
      script.onload = () => {
        console.log('✅ Adobe PDF Embed API script loaded');
        setTimeout(() => initializeAdobeViewer(), 500);
      };
      
      script.onerror = (error) => {
        console.error('❌ Failed to load Adobe PDF Embed API script:', error);
        setError('Failed to load PDF viewer. Please refresh the page.');
      };
      
      document.head.appendChild(script);
    } else {
      console.log('✅ Adobe PDF Embed API already loaded');
      setTimeout(() => initializeAdobeViewer(), 300);
    }
  }, [initializeAdobeViewer]);

  // Load PDF when file changes and Adobe viewer is ready
  useEffect(() => {
    if (!currentFile || !adobeViewerInstanceRef.current) {
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      let url;
      if (currentFile instanceof File || currentFile instanceof Blob) {
        // For uploaded files, create blob URL
        url = URL.createObjectURL(currentFile);
        console.log('📄 Created blob URL for uploaded file:', url);
      } else if (currentFile.backendPath) {
        // Use backend path if available
        const encodedFilename = encodeURIComponent(currentFile.backendPath);
        url = `http://localhost:8000/uploads/${encodedFilename}`;
        console.log('📄 Using backend path URL:', url);
      } else if (currentFile.name) {
        // For file objects with name
        const encodedFilename = encodeURIComponent(currentFile.name);
        url = `http://localhost:8000/uploads/${encodedFilename}`;
        console.log('📄 Using name-based URL:', url);
      } else {
        throw new Error('Invalid file object');
      }

      console.log('📄 Loading PDF with URL:', url);
      
      // Load the PDF using Adobe viewer
      try {
        adobeViewerInstanceRef.current.previewFile({
          content: { location: { url } },
          meta: { fileName: currentFile.name || 'Document.pdf' }
        });
        console.log('✅ PDF loading initiated');
      } catch (error) {
        console.error('❌ Error in previewFile:', error);
        setError('Failed to load PDF in viewer');
        setIsLoading(false);
      }

    } catch (error) {
      console.error('❌ Error loading PDF:', error);
      setError('Failed to load PDF');
      setIsLoading(false);
    }
  }, [currentFile]);

  const handleFileSelect = (selectedFile) => {
    console.log('📁 File selected:', selectedFile.name || selectedFile);
    setCurrentFile(selectedFile);
    setError(null);
    if (onFileSelect) {
      onFileSelect(selectedFile);
    }
  };

  const handleManualTextSubmit = () => {
    if (manualText.trim()) {
      onTextSelection(manualText);
    }
  };

  if (!currentFile) {
    return (
      <PageContainer>
        <div style={{ textAlign: 'center', width: '100%', padding: '40px' }}>
          <h2>No PDF Selected</h2>
          <p>Please upload a PDF file first.</p>
          <ControlButton onClick={onBack}>Go Back</ControlButton>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PDFViewerSection>
        <ViewerHeader>
          <ViewerTitle>
            📄 {currentFile.name || 'Document'}
          </ViewerTitle>
          <ViewerControls>
            <ControlButton onClick={onBack}>
              ← Back
            </ControlButton>
          </ViewerControls>
        </ViewerHeader>
        
        <PDFContainer>
          {/* Always render the Adobe viewer container */}
          <AdobeViewerContainer
            ref={adobeViewerRef}
            id={viewerContainerId}
            style={{ display: error || isLoading ? 'none' : 'block' }}
          />
          
          {/* Show error overlay */}
          {error && (
            <ErrorMessage>
              <h3>❌ PDF Viewer Error</h3>
              <p>{error}</p>
              <button onClick={() => window.location.reload()} style={{ marginTop: '10px', padding: '8px 16px', background: '#667eea', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                Reload Page
              </button>
            </ErrorMessage>
          )}
          
          {/* Show loading overlay */}
          {isLoading && (
            <LoadingSpinner>
              <Spinner />
              <div>Loading PDF...</div>
            </LoadingSpinner>
          )}
        </PDFContainer>
      </PDFViewerSection>
      
      <SidebarSection>
        {/* PDF List Panel */}
        <PDFListPanel>
          <PanelHeader>
            📚 Your PDF Library
          </PanelHeader>
          <PanelContent>
            {uploadedFiles.length > 0 ? (
              <div>
                {uploadedFiles.map((pdf, index) => (
                  <PDFListItem 
                    key={index}
                    active={(currentFile && (currentFile.name || currentFile)) === (pdf.name || pdf)}
                    onClick={() => handleFileSelect(pdf)}
                  >
                    <PDFFileName>{pdf.name || String(pdf)}</PDFFileName>
                    <PDFFileInfo>
                      Uploaded: {pdf.uploaded ? pdf.uploaded.toLocaleDateString() : '—'}
                    </PDFFileInfo>
                  </PDFListItem>
                ))}
              </div>
            ) : (
              <p style={{ color: '#666', fontStyle: 'italic' }}>No PDFs uploaded yet</p>
            )}
          </PanelContent>
        </PDFListPanel>

        {/* Manual Text Input Panel */}
        <SidebarPanel>
          <PanelHeader>
            📝 Manual Text Input
          </PanelHeader>
          <PanelContent>
            <p style={{ marginBottom: '12px', color: '#666' }}>
              Since PDF text selection can be tricky, you can also manually type or paste text here:
            </p>
            <TextInput
              placeholder="Paste your text here or select text in the PDF..."
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
            />
            <GenerateButton
              onClick={handleManualTextSubmit}
              disabled={!manualText.trim() || externalLoading}
            >
              {externalLoading ? 'Generating...' : 'Generate Insights'}
            </GenerateButton>
          </PanelContent>
        </SidebarPanel>
        
        {/* Quick Tips Panel */}
        <SidebarPanel>
          <PanelHeader>
            💡 Quick Tips
          </PanelHeader>
          <PanelContent>
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              <li>Select text directly in the PDF viewer</li>
              <li>Or paste text in the input box above</li>
              <li>Click "Generate Insights" to analyze</li>
              <li>Generate podcasts from the Insights page</li>
              <li>Switch between uploaded PDFs</li>
            </ul>
          </PanelContent>
        </SidebarPanel>
      </SidebarSection>
    </PageContainer>
  );
}

export default PDFViewerPage;
