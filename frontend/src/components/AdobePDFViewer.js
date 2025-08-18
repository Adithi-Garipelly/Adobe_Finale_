import React, { useEffect, useRef, useState, useCallback } from 'react';
import styled from 'styled-components';
import { initializeAdobeViewer, ADOBE_EVENTS } from '../config/adobe-config';

const ViewerContainer = styled.div`
  width: 100%;
  height: 100%;
  min-height: 600px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
  position: relative;
`;

const ViewerHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
`;

const ViewerTitle = styled.div`
  font-size: 16px;
  font-weight: 600;
`;

const ViewerControls = styled.div`
  display: flex;
  gap: 10px;
  align-items: center;
`;

const ControlButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;

const AdobeContainer = styled.div`
  width: 100%;
  height: calc(100% - 60px);
  position: relative;
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
`;

const Spinner = styled.div`
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  color: #dc3545;
  text-align: center;
  padding: 20px;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  margin: 20px;
`;

const SelectionInfo = styled.div`
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 100;
  max-width: 300px;
  word-wrap: break-word;
`;

const AdobePDFViewer = ({ 
  fileUrl, 
  fileName, 
  onTextSelection, 
  onDocumentReady,
  onError,
  showControls = true 
}) => {
  const containerRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewer, setViewer] = useState(null);
  const [apis, setApis] = useState(null);
  const [selectedText, setSelectedText] = useState('');
  const [isAdobeReady, setIsAdobeReady] = useState(false);

  // Check if Adobe DC View SDK is loaded
  useEffect(() => {
    const checkAdobeSDK = () => {
      if (typeof window.AdobeDC !== 'undefined') {
        setIsAdobeReady(true);
        return true;
      }
      return false;
    };

    // Check immediately
    if (checkAdobeSDK()) return;

    // Wait for SDK to load
    const interval = setInterval(() => {
      if (checkAdobeSDK()) {
        clearInterval(interval);
      }
    }, 100);

    // Cleanup
    return () => clearInterval(interval);
  }, []);

  // Initialize Adobe viewer when SDK is ready
  useEffect(() => {
    if (!isAdobeReady || !fileUrl || !containerRef.current) return;

    const initViewer = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const { viewer: newViewer, apis: newApis } = await initializeAdobeViewer(
          containerRef.current.id,
          fileUrl,
          fileName
        );

        setViewer(newViewer);
        setApis(newApis);

        // Set up event listeners
        setupEventListeners(newApis);

        // Notify parent component
        if (onDocumentReady) {
          onDocumentReady(newViewer, newApis);
        }

        setIsLoading(false);

      } catch (err) {
        console.error('Failed to initialize Adobe viewer:', err);
        setError(err.message);
        setIsLoading(false);
        
        if (onError) {
          onError(err);
        }
      }
    };

    initViewer();
  }, [isAdobeReady, fileUrl, fileName, onDocumentReady, onError]);

  // Set up Adobe Embed API event listeners
  const setupEventListeners = useCallback((viewerApis) => {
    if (!viewerApis) return;

    // Text selection events
    viewerApis.addEventListener(ADOBE_EVENTS.SELECTION_START, (event) => {
      console.log('Selection started:', event);
    });

    viewerApis.addEventListener(ADOBE_EVENTS.SELECTION_END, (event) => {
      console.log('Selection ended:', event);
      
      try {
        const selectedContent = event.data?.selectedContent;
        if (selectedContent && selectedContent.length > 0) {
          // Extract text from selection
          const text = selectedContent
            .map(item => item.text || '')
            .filter(text => text.trim())
            .join(' ');

          if (text.trim()) {
            setSelectedText(text);
            
            // Notify parent component
            if (onTextSelection) {
              onTextSelection(text, event.data);
            }
          }
        }
      } catch (err) {
        console.error('Error processing text selection:', err);
      }
    });

    viewerApis.addEventListener(ADOBE_EVENTS.SELECTION_CHANGE, (event) => {
      console.log('Selection changed:', event);
    });

    // Document events
    viewerApis.addEventListener(ADOBE_EVENTS.DOCUMENT_OPEN, (event) => {
      console.log('Document opened:', event);
    });

    viewerApis.addEventListener(ADOBE_EVENTS.PAGE_CHANGE, (event) => {
      console.log('Page changed:', event);
    });

    // Viewer events
    viewerApis.addEventListener(ADOBE_EVENTS.VIEWER_READY, (event) => {
      console.log('Viewer ready:', event);
    });

    viewerApis.addEventListener(ADOBE_EVENTS.VIEWER_ERROR, (event) => {
      console.error('Viewer error:', event);
      setError('PDF viewer encountered an error');
    });

  }, [onTextSelection]);

  // Handle viewer controls
  const handleZoomIn = useCallback(() => {
    if (apis) {
      apis.getZoomAPIs().then(zoomAPIs => {
        zoomAPIs.zoomIn();
      });
    }
  }, [apis]);

  const handleZoomOut = useCallback(() => {
    if (apis) {
      apis.getZoomAPIs().then(zoomAPIs => {
        zoomAPIs.zoomOut();
      });
    }
  }, [apis]);

  const handleFitToWidth = useCallback(() => {
    if (apis) {
      apis.getZoomAPIs().then(zoomAPIs => {
        zoomAPIs.fitToWidth();
      });
    }
  }, [apis]);

  const handleFitToPage = useCallback(() => {
    if (apis) {
      apis.getZoomAPIs().then(zoomAPIs => {
        zoomAPIs.fitToPage();
      });
    }
  }, [apis]);

  // Clear selection info
  const clearSelection = useCallback(() => {
    setSelectedText('');
  }, []);

  // Generate unique container ID
  const containerId = `adobe-pdf-viewer-${Date.now()}`;

  return (
    <ViewerContainer>
      <ViewerHeader>
        <ViewerTitle>
          📄 {fileName || 'PDF Document'}
        </ViewerTitle>
        
        {showControls && (
          <ViewerControls>
            <ControlButton onClick={handleZoomOut} title="Zoom Out">
              🔍-
            </ControlButton>
            <ControlButton onClick={handleZoomIn} title="Zoom In">
              🔍+
            </ControlButton>
            <ControlButton onClick={handleFitToWidth} title="Fit to Width">
              ↔️
            </ControlButton>
            <ControlButton onClick={handleFitToPage} title="Fit to Page">
              📄
            </ControlButton>
          </ViewerControls>
        )}
      </ViewerHeader>

      <AdobeContainer>
        {!isAdobeReady && (
          <LoadingOverlay>
            <Spinner />
            <div>Loading Adobe PDF Embed API...</div>
          </LoadingOverlay>
        )}

        {isAdobeReady && isLoading && (
          <LoadingOverlay>
            <Spinner />
            <div>Loading PDF document...</div>
          </LoadingOverlay>
        )}

        {error && (
          <ErrorMessage>
            <strong>Error:</strong> {error}
            <br />
            <small>Please check the file URL and try again.</small>
          </ErrorMessage>
        )}

        {selectedText && (
          <SelectionInfo>
            <strong>Selected Text:</strong>
            <br />
            {selectedText.length > 100 
              ? `${selectedText.substring(0, 100)}...` 
              : selectedText
            }
            <br />
            <button 
              onClick={clearSelection}
              style={{
                background: 'rgba(255,255,255,0.2)',
                border: 'none',
                color: 'white',
                padding: '2px 6px',
                borderRadius: '2px',
                cursor: 'pointer',
                marginTop: '4px'
              }}
            >
              Clear
            </button>
          </SelectionInfo>
        )}

        <div
          ref={containerRef}
          id={containerId}
          style={{
            width: '100%',
            height: '100%',
            minHeight: '500px'
          }}
        />
      </AdobeContainer>
    </ViewerContainer>
  );
};

export default AdobePDFViewer;
