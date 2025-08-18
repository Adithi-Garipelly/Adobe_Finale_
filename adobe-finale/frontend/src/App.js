import React, { useState, useEffect, useContext } from 'react';
import styled from 'styled-components';
import PDFViewer from './components/PDFViewer';
import FileUpload from './components/FileUpload';
import Header from './components/Header';
import { APIProvider, APIContext } from './context/APIContext';
import { FileProvider } from './context/FileContext';
import { useAPI } from './context/APIContext';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

const MainContent = styled.div`
  display: flex;
  height: calc(100vh - 80px);
  padding: 20px;
  gap: 20px;
`;

const LeftPanel = styled.div`
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const RightPanel = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 400px;
`;

const TabContainer = styled.div`
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 4px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const Tab = styled.button`
  flex: 1;
  padding: 12px 20px;
  border: none;
  background: ${props => props.active ? '#667eea' : 'transparent'};
  color: ${props => props.active ? 'white' : '#666'};
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    background: ${props => props.active ? '#667eea' : '#f0f0f0'};
  }
`;

const PanelContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  height: 100%;
  overflow-y: auto;
`;

const InsightsPanel = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const PodcastPanel = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const PDFListPanel = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
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

function AppContent() {
  const { generateInsights, searchDocuments, getDocuments, deleteDocument } = useAPI();
  const [currentView, setCurrentView] = useState('upload');
  const [selectedText, setSelectedText] = useState('');
  const [insights, setInsights] = useState(null);
  const [relatedSections, setRelatedSections] = useState([]);
  const [podcastData, setPodcastData] = useState(null);
  const [activeTab, setActiveTab] = useState('pdfs');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadedPDFs, setUploadedPDFs] = useState([]);

  // Load uploaded PDFs when component mounts
  useEffect(() => {
    loadUploadedPDFs();
  }, []);

  const loadUploadedPDFs = async () => {
    try {
      console.log("🔄 Loading uploaded PDFs...");
      const response = await getDocuments();
      console.log("📥 Documents response:", response);
      
      if (response.status === 'success') {
        setUploadedPDFs(response.documents);
        console.log("✅ Loaded", response.documents.length, "PDFs");
      } else {
        console.error("❌ Failed to load documents:", response);
      }
    } catch (error) {
      console.error('❌ Error loading documents:', error);
    }
  };

  const handleFileSelect = (file) => {
    console.log("📄 File selected:", file);
    setSelectedFile(file);
    setCurrentView('viewer');
    setActiveTab('insights');
    // Clear any old insights when loading a new PDF
    setInsights(null);
    setRelatedSections([]);
    setSelectedText('');
  };

  const handleDeletePDF = async (docId, filename) => {
    if (window.confirm(`Are you sure you want to delete "${filename}"? This action cannot be undone.`)) {
      try {
        console.log("🗑️ Deleting PDF:", filename, "ID:", docId);
        
        // Call backend to delete PDF using API context
        const result = await deleteDocument(docId);
        
        if (result.status === 'success') {
          console.log("✅ PDF deleted successfully");
          
          // Remove from local state
          setUploadedPDFs(prev => prev.filter(pdf => pdf.id !== docId));
          
          // If this was the currently selected file, clear it and reset state
          if (selectedFile && selectedFile.id === docId) {
            setSelectedFile(null);
            setCurrentView('upload');
            setActiveTab('pdfs');
            // Clear all related data
            setInsights(null);
            setRelatedSections([]);
            setSelectedText('');
          }
          
          // Show success message
          alert(`"${filename}" has been deleted successfully!`);
        } else {
          throw new Error(result.message || 'Failed to delete PDF');
        }
      } catch (error) {
        console.error("❌ Error deleting PDF:", error);
        alert(`Failed to delete "${filename}": ${error.message}`);
      }
    }
  };

  const handleTextSelection = async (text) => {
    if (!text || text.trim().length < 3) {
      console.log("⚠️ Text too short, ignoring selection");
      return;
    }

    // Check if a PDF is currently loaded
    if (!selectedFile) {
      console.log("⚠️ No PDF loaded, cannot generate insights");
      alert("Please load a PDF first before generating insights.");
      return;
    }
    
    console.log("🔍 Text selected:", text);
    setSelectedText(text);
    setIsLoading(true);
    
    try {
      // Use the new universal analyze_selection endpoint
      console.log("🧠 Generating universal insights...");
      const response = await fetch('/api/analyze_selection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const insightsResult = await response.json();
      console.log("🧠 Universal insights response:", insightsResult);
      
      if (insightsResult.status === 'success') {
        // Set the insights in the new format
        setInsights(insightsResult);
        setActiveTab('insights');
        console.log("✅ Universal insights generated successfully");
      } else {
        throw new Error(insightsResult.message || 'Failed to generate insights');
      }
      
    } catch (error) {
      console.error('❌ Error generating insights:', error);
      // Set error insights
      setInsights({
        status: "error",
        relevant_sections: [],
        insights: {
          definition_core_principle: "Error occurred while processing your request",
          application_context: "The system encountered an unexpected error",
          challenges_contradictions: "Please try again or refresh the page",
          model_comparisons: "System error - please try again",
          extensions_other_fields: "Contact support if the issue persists",
          overall_summary: "System error - please try again"
        },
        podcast_transcript: "(Intro Music: Upbeat, tech-focused melody fades in and out)\n\nHost: Hey, we encountered an error while processing your request. Please try again or contact support.",
        error: true,
        error_message: error.message
      });
      setActiveTab('insights');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePDFSelect = (pdf) => {
    setSelectedFile({
      saved_name: pdf.filename,
      original_name: pdf.filename
    });
    setCurrentView('viewer');
  };

  const renderRightPanel = () => {
    switch (activeTab) {
      case 'pdfs':
        return (
          <PDFListPanel>
            <h2 className="text-xl font-semibold mb-4">📚 Your PDF Library</h2>
            {uploadedPDFs.length > 0 ? (
              <div>
                {uploadedPDFs.map((pdf, index) => (
                  <PDFListItem 
                    key={index}
                    active={selectedFile && selectedFile.id === pdf.id}
                    onClick={() => {
                      setSelectedFile(pdf);
                      setCurrentView('viewer');
                      setActiveTab('insights');
                    }}
                  >
                    <div className="flex items-center justify-between w-full">
                      <div className="flex-1">
                        <PDFFileName>{pdf.filename}</PDFFileName>
                        <PDFFileInfo>
                          Uploaded: {new Date(pdf.uploaded_at).toLocaleDateString()}
                        </PDFFileInfo>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation(); // Prevent PDF selection
                          handleDeletePDF(pdf.id, pdf.filename);
                        }}
                        className="ml-2 px-2 py-1 bg-red-500 hover:bg-red-600 text-white text-xs rounded transition-colors"
                        title="Delete PDF"
                      >
                        🗑️
                      </button>
                    </div>
                  </PDFListItem>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No PDFs uploaded yet</p>
            )}
          </PDFListPanel>
        );
      
      case 'insights':
        return (
          <InsightsPanel>
            <h2 className="text-xl font-semibold mb-4">📊 Universal Insights</h2>
            
            {/* Check if PDF is loaded */}
            {!selectedFile ? (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">📄</div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">No PDF Loaded</h3>
                <p className="text-gray-600 mb-6">Please load a PDF first to generate insights.</p>
                <button
                  onClick={() => setCurrentView('upload')}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-colors"
                >
                  Upload PDF
                </button>
              </div>
            ) : isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-gray-600">Generating universal insights...</p>
              </div>
            ) : insights && insights.status === 'success' ? (
              <div>
                <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
                  <h4 className="font-medium text-blue-800 mb-1">Current PDF:</h4>
                  <p className="text-sm text-blue-700">{selectedFile.filename}</p>
                </div>
                
                <div className="mb-4">
                  <h3 className="font-medium mb-2">Selected Text:</h3>
                  <p className="text-sm text-gray-600 bg-gray-100 p-2 rounded">
                    {selectedText}
                  </p>
                </div>
                
                {/* Relevant Sections from Documents */}
                {insights.relevant_sections && insights.relevant_sections.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-3 text-gray-800">🔍 Relevant Sections from Documents</h3>
                    <div className="space-y-3">
                      {insights.relevant_sections.map((section, index) => (
                        <div key={index} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-medium text-gray-900">{section.source}</h4>
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {section.section}
                            </span>
                          </div>
                          <p className="text-sm text-gray-700 leading-relaxed">{section.content}</p>
                          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                            <span>Score: {section.relevance_score?.toFixed(3) || 'N/A'}</span>
                            <span>{section.word_count} words</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Overall Insights (Summary & Connections) */}
                {insights.insights && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold mb-3 text-gray-800">🧠 Overall Insights (Summary & Connections)</h3>
                    <div className="grid gap-3">
                      <div className="bg-green-50 p-3 rounded border border-green-200">
                        <h4 className="font-medium text-green-800 mb-1">Definition & Core Principle:</h4>
                        <p className="text-sm text-green-700">{insights.insights.definition_core_principle}</p>
                      </div>
                      <div className="bg-blue-50 p-3 rounded border border-blue-200">
                        <h4 className="font-medium text-blue-800 mb-1">Application & Context:</h4>
                        <p className="text-sm text-blue-700">{insights.insights.application_context}</p>
                      </div>
                      <div className="bg-yellow-50 p-3 rounded border border-yellow-200">
                        <h4 className="font-medium text-yellow-800 mb-1">Challenges & Contradictions:</h4>
                        <p className="text-sm text-yellow-700">{insights.insights.challenges_contradictions}</p>
                      </div>
                      <div className="bg-purple-50 p-3 rounded border border-purple-200">
                        <h4 className="font-medium text-purple-800 mb-1">Model Comparisons:</h4>
                        <p className="text-sm text-purple-700">{insights.insights.model_comparisons}</p>
                      </div>
                      <div className="bg-indigo-50 p-3 rounded border border-indigo-200">
                        <h4 className="font-medium text-indigo-800 mb-1">Extensions & Other Fields:</h4>
                        <p className="text-sm text-indigo-700">{insights.insights.extensions_other_fields}</p>
                      </div>
                      <div className="bg-gray-50 p-3 rounded border border-gray-200">
                        <h4 className="font-medium text-gray-800 mb-1">Overall Summary:</h4>
                        <p className="text-sm text-gray-700">{insights.insights.overall_summary}</p>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Podcast Transcript */}
                {insights.podcast_transcript && (
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold mb-3 text-gray-800">🎧 Podcast Transcript</h3>
                    <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                      <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
                        {insights.podcast_transcript}
                      </pre>
                    </div>
                  </div>
                )}
                
                <div className="text-sm text-gray-500 text-center">
                  <p>Generated at: {insights.generated_at ? new Date(insights.generated_at).toLocaleString() : 'Just now'}</p>
                  {insights.fallback_mode && (
                    <p className="mt-1">⚠️ Using fallback mode</p>
                  )}
                </div>
              </div>
            ) : insights && insights.error ? (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">⚠️</div>
                <h3 className="text-xl font-medium text-red-900 mb-2">Error Occurred</h3>
                <p className="text-red-600 mb-4">{insights.insights?.overall_summary || 'An error occurred while generating insights'}</p>
                {insights.error_message && (
                  <p className="text-sm text-red-500">Details: {insights.error_message}</p>
                )}
              </div>
            ) : selectedText ? (
              <div className="text-center py-8">
                <p className="text-gray-600 mb-4">Text ready: "{selectedText.substring(0, 100)}..."</p>
                <button 
                  onClick={() => handleTextSelection(selectedText)}
                  disabled={isLoading}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? 'Generating...' : 'Generate Universal Insights'}
                </button>
                <p className="text-sm text-gray-400 mt-2">Click the button above to generate comprehensive insights</p>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">Select text in the PDF or paste it in the input box above</p>
                <p className="text-sm text-gray-400">Tip: Use the text input box above for easy text entry</p>
              </div>
            )}
          </InsightsPanel>
        );
      
      case 'related':
        return (
          <PanelContainer>
            <h2 className="text-xl font-semibold mb-4">🔍 Related Sections</h2>
            {relatedSections.length > 0 ? (
              <div className="space-y-3">
                {relatedSections.map((section, index) => (
                  <div key={index} className="border rounded-lg p-3 bg-gray-50">
                    <h4 className="font-medium text-sm">{section.filename}</h4>
                    <p className="text-sm text-gray-600 mt-1">{section.content_preview}</p>
                    <div className="text-xs text-gray-500 mt-2">
                      Score: {section.score} | Uploaded: {new Date(section.uploaded_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No related sections found</p>
            )}
          </PanelContainer>
        );
      
      case 'podcast':
        return (
          <PodcastPanel>
            <h2 className="text-xl font-semibold mb-4">🎧 Podcast</h2>
            {podcastData ? (
              <div>
                <p className="text-gray-600 mb-4">{podcastData.message}</p>
                {podcastData.audio_url && (
                  <audio controls className="w-full">
                    <source src={`http://localhost:8080${podcastData.audio_url}`} type="audio/mpeg" />
                    Your browser does not support the audio element.
                  </audio>
                )}
              </div>
            ) : (
              <div>
                <p className="text-gray-500 mb-4">Podcast generation coming soon!</p>
                <button 
                  onClick={handleGeneratePodcast}
                  disabled={!selectedText || isLoading}
                  className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
                >
                  {isLoading ? 'Generating...' : 'Generate Podcast'}
                </button>
              </div>
            )}
          </PodcastPanel>
        );
      
      default:
        return (
          <PanelContainer>
            <p className="text-gray-500">Select a tab to view content</p>
          </PanelContainer>
        );
    }
  };

  const handleGeneratePodcast = async () => {
    if (!selectedText) {
      alert("Please enter some text first!");
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8080/podcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selected_text: selectedText,
          k: 8, // Get more context for better podcast
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setPodcastData(data);
        setActiveTab('podcast');
      }
    } catch (error) {
      console.error('Error generating podcast:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AppContainer>
      <Header />
      
      {/* Manual Text Input Section - Integrated into the main layout */}
      <MainContent>
        <LeftPanel>
          {currentView === 'upload' ? (
            <FileUpload onUploadComplete={handleFileSelect} />
          ) : (
            <PDFViewer 
              file={selectedFile} 
              onTextSelection={handleTextSelection}
              isLoading={isLoading}
            />
          )}
        </LeftPanel>
        <RightPanel>
          {/* Quick Text Input for Insights */}
          <div className="mb-4 p-3 bg-gray-50 rounded border border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-2">🔍 Quick Insights</h3>
            
            {/* Show current PDF status */}
            {selectedFile ? (
              <div className="mb-2 p-2 bg-green-50 border border-green-200 rounded text-xs">
                <span className="text-green-700">📄 Current PDF: {selectedFile.filename}</span>
              </div>
            ) : (
              <div className="mb-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs">
                <span className="text-yellow-700">⚠️ No PDF loaded - please upload one first</span>
              </div>
            )}
            
            <div className="flex gap-2">
              <textarea
                placeholder={selectedFile ? "Paste text here to generate insights..." : "Upload a PDF first to generate insights..."}
                value={selectedText}
                onChange={(e) => setSelectedText(e.target.value)}
                className="flex-1 p-2 text-sm border border-gray-300 rounded resize-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                rows="2"
                disabled={!selectedFile}
              />
              <button
                onClick={() => handleTextSelection(selectedText)}
                disabled={!selectedFile || !selectedText.trim() || selectedText.trim().length < 3 || isLoading}
                className="px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
              >
                {isLoading ? '...' : 'Go'}
              </button>
            </div>
            
            {!selectedFile && (
              <p className="text-xs text-gray-500 mt-2">
                💡 Upload a PDF first, then paste text here to generate insights
              </p>
            )}
          </div>
          
          <TabContainer>
            <Tab 
              active={activeTab === 'pdfs'} 
              onClick={() => setActiveTab('pdfs')}
            >
              📚 PDFs
            </Tab>
            <Tab 
              active={activeTab === 'insights'} 
              onClick={() => setActiveTab('insights')}
            >
              📊 Insights
            </Tab>
            <Tab 
              active={activeTab === 'related'} 
              onClick={() => setActiveTab('related')}
            >
              🔍 Related
            </Tab>
            <Tab 
              active={activeTab === 'podcast'} 
              onClick={() => setActiveTab('podcast')}
            >
              🎧 Podcast
            </Tab>
          </TabContainer>
          
          {renderRightPanel()}
        </RightPanel>
      </MainContent>
    </AppContainer>
  );
}

function App() {
  return (
    <APIProvider>
      <FileProvider>
        <AppContent />
      </FileProvider>
    </APIProvider>
  );
}

export default App;
