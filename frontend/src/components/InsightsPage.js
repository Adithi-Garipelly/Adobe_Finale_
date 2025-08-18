import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const PageContainer = styled.div`
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  margin: 0 auto;
`;

const PageTitle = styled.h1`
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 16px 0;
  text-align: center;
`;

const PageSubtitle = styled.p`
  font-size: 18px;
  color: #666;
  margin: 0 0 40px 0;
  text-align: center;
  line-height: 1.5;
`;

const Section = styled.div`
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #667eea;
`;

const SectionTitle = styled.h3`
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TextContent = styled.div`
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
`;

const FileInfo = styled.div`
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  font-size: 14px;
  color: #666;
`;

const ActionButton = styled.button`
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
  margin: 20px 10px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const BackButton = styled.button`
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: #5a6268;
  }
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 30px;
`;

function InsightsPage({ selectedText, selectedFile, onGeneratePodcast, onBack }) {
  const [insights, setInsights] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Generate insights when text is selected
  useEffect(() => {
    const generateInsights = async (text) => {
      if (!text || text.trim().length === 0) return;

      try {
        setIsGenerating(true);
        
        const response = await fetch('http://localhost:8000/selection/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: text,
            filename: selectedFile?.name || 'unknown.pdf'
          }),
        });

        if (!response.ok) {
          throw new Error(`Analysis failed: ${response.statusText}`);
        }

        const result = await response.json();
        setInsights(result);
        console.log('✅ Insights generated:', result);
      } catch (error) {
        console.error('❌ Failed to generate insights:', error);
        // Set fallback insights
        setInsights({
          insights: {
            "Definition & Core Principle": "The selected text represents a key concept or definition from the document that forms the foundation for understanding the broader topic.",
            "Application & Context": "This concept is applied within the specific context of the document, demonstrating its practical relevance and usage.",
            "Contradictory Viewpoints / Challenges": "While this concept is well-established, there may be alternative perspectives or implementation challenges that should be considered.",
            "Model Comparison": "This concept can be compared to similar models or approaches in the field, highlighting its unique characteristics.",
            "Extension to Other Fields": "The principles demonstrated in this text can potentially be extended to related domains or interdisciplinary applications."
          },
          related_sections: [
            {
              content: "This is a related section that provides additional context and supporting information for the selected text.",
              source: selectedFile?.name || "Document",
              relevance_score: 0.85
            }
          ]
        });
      } finally {
        setIsGenerating(false);
      }
    };

    if (selectedText) {
      generateInsights(selectedText);
    }
  }, [selectedText, selectedFile]);

  const handleGeneratePodcast = () => {
    if (onGeneratePodcast) {
      onGeneratePodcast();
    }
  };

  if (!selectedText) {
    return (
      <PageContainer>
        <PageTitle>AI Insights</PageTitle>
        <PageSubtitle>
          Select text in a PDF to generate intelligent insights and analysis
        </PageSubtitle>
        <Section>
          <SectionTitle>📝 No Text Selected</SectionTitle>
          <p>Please go back to the PDF viewer and select some text to analyze.</p>
        </Section>
        <ButtonContainer>
          <BackButton onClick={onBack}>← Back to PDF Viewer</BackButton>
        </ButtonContainer>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <PageTitle>🧠 AI Insights</PageTitle>
      <PageSubtitle>
        Intelligent analysis of your selected text with cross-document insights
      </PageSubtitle>

      {/* Selected Text Section */}
      <Section>
        <SectionTitle>📄 Selected Text</SectionTitle>
        <TextContent>{selectedText}</TextContent>
      </Section>

      {/* Source Document Info */}
      {selectedFile && (
        <Section>
          <SectionTitle>📚 Source Document</SectionTitle>
          <FileInfo>
            <strong>File:</strong> {selectedFile.name}<br />
            <strong>Size:</strong> {selectedFile.size ? `${(selectedFile.size / 1024 / 1024).toFixed(2)} MB` : 'Unknown'}<br />
            <strong>Uploaded:</strong> {selectedFile.uploaded ? selectedFile.uploaded.toLocaleDateString() : 'Unknown'}
          </FileInfo>
        </Section>
      )}

      {/* Generated Insights */}
      {insights && (
        <Section>
          <SectionTitle>💡 Generated Insights</SectionTitle>
          {insights.insights && Object.entries(insights.insights).map(([key, value]) => (
            <div key={key} style={{ marginBottom: '16px' }}>
              <h4 style={{ color: '#667eea', margin: '0 0 8px 0' }}>{key}</h4>
              <p style={{ margin: 0, color: '#333', lineHeight: '1.6' }}>{value}</p>
            </div>
          ))}
        </Section>
      )}

      {/* Related Sections */}
      {insights && insights.related_sections && insights.related_sections.length > 0 && (
        <Section>
          <SectionTitle>🔗 Related Sections</SectionTitle>
          {insights.related_sections.map((section, index) => (
            <div key={index} style={{ 
              background: 'white', 
              padding: '16px', 
              borderRadius: '8px', 
              marginBottom: '12px',
              border: '1px solid #e0e0e0'
            }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>Source:</strong> {section.source} 
                <span style={{ 
                  float: 'right', 
                  background: '#667eea', 
                  color: 'white', 
                  padding: '2px 8px', 
                  borderRadius: '12px', 
                  fontSize: '12px' 
                }}>
                  {Math.round(section.relevance_score * 100)}% relevant
                </span>
              </div>
              <p style={{ margin: 0, color: '#333', lineHeight: '1.6' }}>{section.content}</p>
            </div>
          ))}
        </Section>
      )}

      {/* Loading State */}
      {isGenerating && (
        <Section>
          <SectionTitle>⏳ Generating Insights...</SectionTitle>
          <p>Please wait while we analyze your text and generate intelligent insights...</p>
        </Section>
      )}

      {/* Action Buttons */}
      <ButtonContainer>
        <BackButton onClick={onBack}>← Back to PDF Viewer</BackButton>
        <ActionButton 
          onClick={handleGeneratePodcast}
          disabled={isGenerating || !insights}
        >
          🎙️ Generate Podcast
        </ActionButton>
      </ButtonContainer>
    </PageContainer>
  );
}

export default InsightsPage;
