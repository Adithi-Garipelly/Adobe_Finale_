import React, { useEffect, useState } from "react";
import UploadPage from "./components/UploadPage";
import LibraryPage from "./components/LibraryPage";
import ViewerPage from "./components/ViewerPage";
import axios from "axios";

const API = process.env.REACT_APP_API || "http://localhost:8000";

export default function App() {
  const [page, setPage] = useState("upload");
  const [files, setFiles] = useState([]);
  const [selected, setSelected] = useState(null);

  async function refreshFiles() {
    const { data } = await axios.get(`${API}/files`);
    setFiles(data.files || []);
  }

  useEffect(() => {
    refreshFiles();
  }, []);

  return (
    <div>
      {page === "upload" && (
        <UploadPage
          onUploaded={async () => {
            await refreshFiles();
            setPage("library");
          }}
        />
      )}
      {page === "library" && (
        <LibraryPage
          files={files}
          onBackToUpload={() => setPage("upload")}
          onOpen={(f) => {
            setSelected(f);
            setPage("viewer");
          }}
        />
      )}
      {page === "viewer" && (
        <ViewerPage
          apiBase={API}
          fileName={selected}
          onBack={() => setPage("library")}
        />
      )}
    </div>
  );
}
