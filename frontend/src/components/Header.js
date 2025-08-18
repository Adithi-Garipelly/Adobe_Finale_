import React from 'react';
import styled from 'styled-components';

const HeaderContainer = styled.header`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
`;

const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
`;

const TitleSection = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Title = styled.h1`
  font-size: 24px;
  font-weight: 600;
  margin: 0;
`;

const TitleIcon = styled.div`
  font-size: 28px;
  opacity: 0.9;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
`;

const HeaderButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.25);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const ButtonIcon = styled.span`
  font-size: 16px;
`;

function Header({ onUpload }) {
  const handleUploadClick = () => {
    // Trigger file upload
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf';
    input.multiple = false;
    input.onchange = (e) => {
      if (e.target.files[0]) {
        onUpload(e.target.files[0]);
      }
    };
    input.click();
  };

  const handleFilesClick = () => {
    // Show files list or trigger file selection
    alert('Files functionality coming soon!');
  };

  return (
    <HeaderContainer>
      <HeaderContent>
        <TitleSection>
          <TitleIcon>📊</TitleIcon>
          <Title>Web App Demo</Title>
        </TitleSection>
        
        <ButtonGroup>
          <HeaderButton onClick={handleUploadClick}>
            <ButtonIcon>⬆️</ButtonIcon>
            Upload
          </HeaderButton>
          
          <HeaderButton onClick={handleFilesClick}>
            <ButtonIcon>☰</ButtonIcon>
            Files
          </HeaderButton>
        </ButtonGroup>
      </HeaderContent>
    </HeaderContainer>
  );
}

export default Header;
