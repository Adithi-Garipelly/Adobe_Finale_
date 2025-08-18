import React from 'react';
import styled from 'styled-components';

const PageContainer = styled.div`
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
`;

const PageHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
`;

const HeaderTitle = styled.h1`
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #333;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 12px;
`;

const ActionButton = styled.button`
  background: ${props => props.primary ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#6c757d'};
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }
`;

const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
`;

const ContentSection = styled.div`
  background: #f8f9fa;
  border-radius: 12px;
  padding: 24px;
  border-left: 4px solid #667eea;
`;

const SectionTitle = styled.h3`
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SectionContent = styled.div`
  color: #555;
  line-height: 1.6;
  font-size: 14px;
`;

const PodcastContainer = styled.div`
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  border-radius: 12px;
  padding: 30px;
  border: 2px solid #e8f2ff;
  text-align: center;
`;

const PodcastTitle = styled.h2`
  margin: 0 0 24px 0;
  font-size: 22px;
  font-weight: 700;
  color: #333;
`;

const AudioPlayer = styled.div`
  margin: 20px 0;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const AudioControls = styled.audio`
  width: 100%;
  height: 50px;
`;

const DownloadButton = styled.a`
  display: inline-block;
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  text-decoration: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  margin: 10px;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
  }
`;

const TranscriptContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: left;
`;

const TranscriptTitle = styled.h4`
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TranscriptContent = styled.pre`
  background: #f8f9fa;
  padding: 16px;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: #555;
  white-space: pre-wrap;
  overflow-x: auto;
  margin: 0;
`;

const SuccessIcon = styled.div`
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.8;
`;

const SuccessMessage = styled.p`
  font-size: 16px;
  color: #666;
  margin-bottom: 20px;
`;

function PodcastPage({ podcastData, selectedText, insights, onBack, onBackToViewer }) {
  if (!podcastData) {
    return (
      <PageContainer>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <h2>No Podcast Data</h2>
          <p>Please generate a podcast first.</p>
          <ActionButton onClick={onBack}>Go Back</ActionButton>
        </div>
      </PageContainer>
    );
  }

  const audioUrl = `http://localhost:8000${podcastData.mp3_url}`;
  const transcriptUrl = `http://localhost:8000${podcastData.transcript_url}`;

  return (
    <PageContainer>
      <PageHeader>
        <HeaderTitle>
          🎧 Podcast Generated Successfully!
        </HeaderTitle>
        <HeaderActions>
          <ActionButton onClick={onBack}>
            ← Back to Insights
          </ActionButton>
          <ActionButton onClick={onBackToViewer}>
            ← Back to Viewer
          </ActionButton>
        </HeaderActions>
      </PageHeader>

      <ContentGrid>
        <ContentSection>
          <SectionTitle>
            📄 Source Text
          </SectionTitle>
          <SectionContent>
            {selectedText ? (
              <div style={{ 
                background: '#e3f2fd', 
                padding: '16px', 
                borderRadius: '8px',
                border: '1px solid #bbdefb'
              }}>
                "{selectedText.length > 200 ? `${selectedText.substring(0, 200)}...` : selectedText}"
              </div>
            ) : (
              <em>No text selected</em>
            )}
          </SectionContent>
        </ContentSection>

        <ContentSection>
          <SectionTitle>
            📚 Source Document
          </SectionTitle>
          <SectionContent>
            <strong>File:</strong> {insights?.source_document || 'Unknown'}<br />
            <strong>Generated:</strong> {new Date().toLocaleString()}<br />
            <strong>Audio Format:</strong> MP3 (High Quality)
          </SectionContent>
        </ContentSection>
      </ContentGrid>

      <PodcastContainer>
        <SuccessIcon>🎉</SuccessIcon>
        <PodcastTitle>Your Podcast is Ready!</PodcastTitle>
        <SuccessMessage>
          The AI has successfully generated a podcast from your selected text using Azure TTS.
        </SuccessMessage>

        <AudioPlayer>
          <h4 style={{ margin: '0 0 16px 0', color: '#333' }}>🎙️ Listen to Your Podcast</h4>
          <AudioControls controls>
            <source src={audioUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </AudioControls>
        </AudioPlayer>

        <div>
          <DownloadButton href={audioUrl} download="podcast.mp3">
            📥 Download MP3
          </DownloadButton>
          <DownloadButton href={transcriptUrl} download="transcript.txt">
            📄 Download Transcript
          </DownloadButton>
        </div>

        <TranscriptContainer>
          <TranscriptTitle>
            📝 Podcast Transcript
          </TranscriptTitle>
          <TranscriptContent>
            {insights?.insights || selectedText || 'Transcript content will appear here...'}
          </TranscriptContent>
        </TranscriptContainer>
      </PodcastContainer>
    </PageContainer>
  );
}

export default PodcastPage;
