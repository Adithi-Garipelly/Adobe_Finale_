import React, { useState } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API || "http://localhost:8080";

export default function UploadPage({ onUploaded }) {
  const [files, setFiles] = useState([]);
  const [busy, setBusy] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const tooMany = files.length > 50;

  async function doUpload() {
    if (files.length === 0 || tooMany) return;
    console.log("Starting upload with files:", files);
    setBusy(true);
    setIndexing(false);
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f));
    try {
      console.log("Uploading to:", `${API}/upload`);
      const response = await axios.post(`${API}/upload`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      console.log("Upload response:", response.data);
      
      // Show indexing status
      if (response.data.message && response.data.message.includes("Indexing")) {
        setIndexing(true);
        console.log("Showing indexing status, will call onUploaded in 2 seconds");
        // Wait a bit then proceed (indexing happens in background)
        setTimeout(() => {
          console.log("Calling onUploaded()");
          setIndexing(false);
          onUploaded();
        }, 2000);
      } else {
        console.log("No indexing message, calling onUploaded immediately");
        onUploaded();
      }
    } catch (e) {
      console.error("Upload error:", e);
      alert("Upload failed. See console.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ 
      padding: '40px', 
      maxWidth: '600px', 
      margin: '0 auto',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <h1 style={{ 
        fontSize: '32px', 
        fontWeight: '600', 
        color: '#1a1a1a', 
        marginBottom: '8px',
        textAlign: 'center'
      }}>
        Upload PDFs
      </h1>
      <p style={{ 
        fontSize: '16px', 
        color: '#666', 
        marginBottom: '40px',
        textAlign: 'center'
      }}>
        Select up to 50 PDF files to analyze
      </p>
      
      <div style={{
        border: '2px dashed #e1e5e9',
        borderRadius: '12px',
        padding: '40px',
        textAlign: 'center',
        backgroundColor: '#fafbfc',
        marginBottom: '24px',
        transition: 'all 0.2s ease',
        position: 'relative'
      }}>
        <input
          type="file"
          accept="application/pdf"
          multiple
          onChange={(e) => {
            console.log("File input changed:", e.target.files);
            setFiles(Array.from(e.target.files));
          }}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            opacity: 0,
            cursor: 'pointer',
            zIndex: 10
          }}
        />
        <div style={{ fontSize: '48px', marginBottom: '16px' }}>📄</div>
        <div style={{ fontSize: '18px', color: '#1a1a1a', marginBottom: '8px' }}>
          {files.length > 0 ? `${files.length} file(s) selected` : 'Click to select PDF files'}
        </div>
        <div style={{ fontSize: '14px', color: '#666' }}>
          Drag and drop or click to browse
        </div>
      </div>
      
      <button 
        onClick={doUpload} 
        disabled={busy || files.length === 0 || tooMany}
        style={{
          width: '100%',
          padding: '16px 24px',
          fontSize: '16px',
          fontWeight: '600',
          backgroundColor: busy || files.length === 0 || tooMany ? '#e1e5e9' : '#0070f3',
          color: busy || files.length === 0 || tooMany ? '#999' : 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: busy || files.length === 0 || tooMany ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s ease'
        }}
      >
        {busy ? "Uploading..." : "Upload Files"}
      </button>
      
      {files.length > 0 && (
        <div style={{ 
          marginTop: '16px', 
          padding: '16px', 
          backgroundColor: '#f0f9ff', 
          borderRadius: '8px',
          border: '1px solid #bae6fd'
        }}>
          <div style={{ fontSize: '14px', color: '#0369a1' }}>
            📁 {files.length} file(s) ready to upload
          </div>
        </div>
      )}
      
      {tooMany && (
        <div style={{ 
          marginTop: '16px', 
          padding: '16px', 
          backgroundColor: '#fef2f2', 
          borderRadius: '8px',
          border: '1px solid #fecaca',
          color: '#dc2626'
        }}>
          ⚠️ Maximum 50 files allowed
        </div>
      )}
      
      {indexing && (
        <div style={{ 
          marginTop: '16px', 
          padding: '16px', 
          backgroundColor: '#f0f9ff', 
          borderRadius: '8px',
          border: '1px solid #bae6fd',
          color: '#0369a1'
        }}>
          🔄 Indexing files for search... This may take a few moments.
        </div>
      )}
    </div>
  );
}
