import React from "react";

export default function LibraryPage({ files, onOpen, onBackToUpload }) {
  return (
    <div style={{ padding: 24 }}>
      <h2>Your Library</h2>
      <button onClick={onBackToUpload}>+ Add more PDFs</button>
      <ul>
        {files.map((f) => (
          <li key={f} style={{ margin: "8px 0" }}>
            <span>{f}</span>
            <button style={{ marginLeft: 12 }} onClick={() => onOpen(f)}>
              Open
            </button>
          </li>
        ))}
      </ul>
      {files.length === 0 && <div>No PDFs yet. Go upload some!</div>}
    </div>
  );
}
