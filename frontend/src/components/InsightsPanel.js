import React from 'react';
import styled from 'styled-components';

const PanelContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const PanelHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
`;

const PanelTitle = styled.h3`
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RefreshButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: #f0f0f0;
  }
`;

const PanelContent = styled.div`
  color: #666;
  font-size: 14px;
  line-height: 1.5;
`;

const AIInsightsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const InsightSection = styled.div`
  border: 2px solid;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
`;

const SelectedTextSection = styled(InsightSection)`
  border-color: #3b82f6;
`;

const KeyInsightsSection = styled(InsightSection)`
  border-color: #f59e0b;
`;

const SectionHeader = styled.h4`
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const SelectedTextHeader = styled(SectionHeader)`
  color: #3b82f6;
`;

const KeyInsightsHeader = styled(SectionHeader)`
  color: #f59e0b;
`;

const SectionContent = styled.div`
  font-size: 13px;
  line-height: 1.4;
`;

const SelectedTextContent = styled(SectionContent)`
  color: #3b82f6;
`;

const KeyInsightsContent = styled(SectionContent)`
  color: #333;
`;

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const Spinner = styled.div`
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

function InsightsPanel({ insights, selectedText, onRefresh, isLoading }) {
  return (
    <>
      {/* Top Panel: Insights */}
      <PanelContainer>
        <PanelHeader>
          <PanelTitle>
            📊 Insights
          </PanelTitle>
          <RefreshButton onClick={onRefresh} title="Refresh insights">
            🔄
          </RefreshButton>
        </PanelHeader>
        <PanelContent>
          {!insights ? (
            "Click refresh to generate insights about this document."
          ) : (
            "Insights generated successfully! Check the AI Insights panel below for detailed analysis."
          )}
        </PanelContent>
      </PanelContainer>

      {/* Bottom Panel: AI Insights */}
      <PanelContainer>
        <PanelHeader>
          <PanelTitle>
            📊 AI Insights
          </PanelTitle>
        </PanelHeader>
        
        <AIInsightsContainer>
          {/* Selected Text Section */}
          <SelectedTextSection>
            <SelectedTextHeader>
              📄 Selected Text
            </SelectedTextHeader>
            <SelectedTextContent>
              {selectedText ? (
                selectedText.length > 100 
                  ? `${selectedText.substring(0, 100)}...` 
                  : selectedText
              ) : (
                "Selected text will appear here when you highlight content in the document."
              )}
            </SelectedTextContent>
          </SelectedTextSection>

          {/* Key Insights & Analysis Section */}
          <KeyInsightsSection>
            <KeyInsightsHeader>
              📊 Key Insights & Analysis
            </KeyInsightsHeader>
            <KeyInsightsContent>
              {isLoading ? (
                <LoadingSpinner>
                  <Spinner />
                </LoadingSpinner>
              ) : insights ? (
                <div>
                  {insights.insights && (
                    <div style={{ marginBottom: '16px' }}>
                      <strong>Generated Insights:</strong>
                      <div style={{ marginTop: '8px', padding: '8px', background: '#f0f9ff', borderRadius: '4px' }}>
                        {insights.insights}
                      </div>
                    </div>
                  )}
                  
                  {insights.related_sections && insights.related_sections.length > 0 && (
                    <div>
                      <strong>Related Sections:</strong>
                      <div style={{ marginTop: '8px' }}>
                        {insights.related_sections.slice(0, 3).map((section, index) => (
                          <div key={index} style={{ 
                            padding: '8px', 
                            marginBottom: '8px', 
                            background: '#fef3c7', 
                            borderRadius: '4px',
                            fontSize: '12px'
                          }}>
                            <strong>{section.document_name}</strong>: {section.content.substring(0, 80)}...
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                "AI insights will be generated here based on the selected text and document content."
              )}
            </KeyInsightsContent>
          </KeyInsightsSection>
        </AIInsightsContainer>
      </PanelContainer>
    </>
  );
}

export default InsightsPanel;
