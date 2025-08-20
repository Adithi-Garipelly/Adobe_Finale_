import React from "react";

export default function LibraryPage({ files, onOpen, onBackToUpload }) {
  return (
    <div style={{ 
      padding: '40px', 
      maxWidth: '800px', 
      margin: '0 auto',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '32px'
      }}>
        <h1 style={{ 
          fontSize: '32px', 
          fontWeight: '600', 
          color: '#1a1a1a', 
          margin: 0
        }}>
          Your Library
        </h1>
        <button 
          onClick={onBackToUpload}
          style={{
            padding: '12px 20px',
            fontSize: '14px',
            fontWeight: '600',
            backgroundColor: '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span>+</span> Add more PDFs
        </button>
      </div>
      
      {files.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: '#666'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📚</div>
          <div style={{ fontSize: '18px', marginBottom: '8px' }}>No PDFs yet</div>
          <div style={{ fontSize: '14px' }}>Go upload some files to get started!</div>
        </div>
      ) : (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          border: '1px solid #e1e5e9',
          overflow: 'hidden'
        }}>
          {files.map((f, index) => (
            <div 
              key={f} 
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '16px 20px',
                borderBottom: index < files.length - 1 ? '1px solid #f0f0f0' : 'none',
                backgroundColor: index % 2 === 0 ? '#fafbfc' : 'white',
                transition: 'background-color 0.2s ease'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                flex: 1
              }}>
                <div style={{ fontSize: '20px' }}>📄</div>
                <span style={{
                  fontSize: '14px',
                  color: '#1a1a1a',
                  fontWeight: '500'
                }}>
                  {f}
                </span>
              </div>
              <button 
                onClick={() => onOpen(f)}
                style={{
                  padding: '8px 16px',
                  fontSize: '13px',
                  fontWeight: '600',
                  backgroundColor: '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  whiteSpace: 'nowrap'
                }}
              >
                Open
              </button>
            </div>
          ))}
        </div>
      )}
      
      {files.length > 0 && (
        <div style={{
          marginTop: '20px',
          textAlign: 'center',
          fontSize: '14px',
          color: '#666'
        }}>
          {files.length} PDF file{files.length !== 1 ? 's' : ''} in your library
        </div>
      )}
    </div>
  );
}
