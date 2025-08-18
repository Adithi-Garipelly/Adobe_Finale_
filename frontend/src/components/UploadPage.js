import React, { useState } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API || "http://localhost:8000";

export default function UploadPage({ onUploaded }) {
  const [files, setFiles] = useState([]);
  const [busy, setBusy] = useState(false);
  const tooMany = files.length > 50;

  async function doUpload() {
    if (files.length === 0 || tooMany) return;
    setBusy(true);
    const fd = new FormData();
    files.forEach((f) => fd.append("files", f));
    try {
      await axios.post(`${API}/upload`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onUploaded();
    } catch (e) {
      alert("Upload failed. See console.");
      console.error(e);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <h2>Upload PDFs (up to 50)</h2>
      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={(e) => setFiles(Array.from(e.target.files))}
      />
      <div style={{ marginTop: 12 }}>
        <button onClick={doUpload} disabled={busy || files.length === 0 || tooMany}>
          {busy ? "Uploading..." : "Upload"}
        </button>
      </div>
      <div style={{ marginTop: 12 }}>
        {files.length > 0 && <div>Selected: {files.length} file(s)</div>}
        {tooMany && <div style={{ color: "red" }}>Max 50 files allowed.</div>}
      </div>
    </div>
  );
}
