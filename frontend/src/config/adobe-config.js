// Adobe Embed API Configuration
export const ADOBE_CONFIG = {
  // Your Adobe Embed API credentials
  CLIENT_ID: '1d691dca47814a4d847ab3286df17a8e',
  
  // Adobe Embed API settings
  EMBED_MODE: 'SIZED_CONTAINER', // or 'FULL_WINDOW', 'LIGHT_BOX'
  
  // Viewer settings
  SHOW_DOWNLOAD_PDF: false,
  SHOW_PRINT_PDF: false,
  SHOW_LEFT_PANEL: true,
  SHOW_ANNOTATION_TOOLS: true,
  
  // Theme and appearance
  THEME: 'light', // 'light' or 'dark'
  
  // Default viewer dimensions
  DEFAULT_WIDTH: '100%',
  DEFAULT_HEIGHT: '600px'
};

// Adobe Embed API event handlers
export const ADOBE_EVENTS = {
  // Text selection events
  SELECTION_START: 'SELECTION_START',
  SELECTION_END: 'SELECTION_END',
  SELECTION_CHANGE: 'SELECTION_CHANGE',
  
  // Document events
  DOCUMENT_OPEN: 'DOCUMENT_OPEN',
  DOCUMENT_CLOSE: 'DOCUMENT_CLOSE',
  PAGE_CHANGE: 'PAGE_CHANGE',
  
  // Viewer events
  VIEWER_READY: 'VIEWER_READY',
  VIEWER_ERROR: 'VIEWER_ERROR'
};

// Adobe Embed API initialization function
export const initializeAdobeViewer = (containerId, fileUrl, fileName) => {
  return new Promise((resolve, reject) => {
    // Check if Adobe DC View SDK is available
    if (typeof window.AdobeDC === 'undefined') {
      reject(new Error('Adobe DC View SDK not loaded'));
      return;
    }

    try {
      // Create Adobe DC View instance
      const adobeDCView = new window.AdobeDC.View({
        clientId: ADOBE_CONFIG.CLIENT_ID,
        divId: containerId
      });

      // Preview file with configuration
      adobeDCView.previewFile(
        {
          content: { 
            location: { url: fileUrl } 
          },
          metaData: { 
            fileName: fileName || 'Document.pdf' 
          }
        },
        { 
          embedMode: ADOBE_CONFIG.EMBED_MODE,
          showDownloadPDF: ADOBE_CONFIG.SHOW_DOWNLOAD_PDF,
          showPrintPDF: ADOBE_CONFIG.SHOW_PRINT_PDF,
          showLeftPanel: ADOBE_CONFIG.SHOW_LEFT_PANEL,
          showAnnotationTools: ADOBE_CONFIG.SHOW_ANNOTATION_TOOLS
        }
      ).then((viewer) => {
        // Get APIs and set up event listeners
        viewer.getAPIs().then((apis) => {
          resolve({ viewer, apis });
        }).catch(reject);
      }).catch(reject);

    } catch (error) {
      reject(error);
    }
  });
};
