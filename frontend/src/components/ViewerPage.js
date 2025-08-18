import React, { useEffect, useRef, useState, useCallback } from "react";
import axios from "axios";

const ADOBE_KEY = process.env.REACT_APP_ADOBE_EMBED_API_KEY; // put in .env
const SDK_URL = "https://documentcloud.adobe.com/view-sdk/main.js";

export default function ViewerPage({ apiBase, fileName, onBack }) {
  const containerRef = useRef(null);
  const [adobeReady, setAdobeReady] = useState(false);
  const [error, setError] = useState("");
  const [manualText, setManualText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Chat functionality
  const [question, setQuestion] = useState("");
  const [chatAnswer, setChatAnswer] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");

  // Wrap analyze function in useCallback to prevent infinite re-renders
  const analyze = useCallback(async (text) => {
    setLoading(true);
    setResult(null);
    try {
      const { data } = await axios.post(`${apiBase}/analyze_selection`, {
        current_pdf: fileName,
        selected_text: text,
        max_sections: 5,
      });
      setResult(data);
    } catch (e) {
      console.error(e);
      setError("Analysis failed");
    } finally {
      setLoading(false);
    }
  }, [apiBase, fileName]);

  // Chat function
  const askQuestion = async () => {
    if (!question.trim() || !fileName) return;
    
    setChatLoading(true);
    setChatAnswer("");
    setAudioUrl("");
    
    try {
      // Ask Gemini about the PDF
      const chatResponse = await axios.post(`${apiBase}/chat/ask`, {
        question: question.trim(),
        pdf_name: fileName
      });
      
      setChatAnswer(chatResponse.data.answer);
      
      // Generate speech using Azure TTS
      const ttsForm = new FormData();
      ttsForm.append("text", chatResponse.data.answer);
      
      const ttsResponse = await axios.post(`${apiBase}/chat/speak`, ttsForm, {
        responseType: "blob"
      });
      
      const audioBlob = new Blob([ttsResponse.data], { type: "audio/mpeg" });
      const audioUrl = URL.createObjectURL(audioBlob);
      setAudioUrl(audioUrl);
      
    } catch (e) {
      console.error("Chat error:", e);
      setChatAnswer("Sorry, I couldn't process your question. Please try again.");
    } finally {
      setChatLoading(false);
    }
  };

  // Load SDK once
  useEffect(() => {
    function onSdkReady() {
      setAdobeReady(true);
    }
    if (!window.AdobeDC) {
      const s = document.createElement("script");
      s.src = SDK_URL;
      s.async = true;
      s.onload = onSdkReady;
      s.onerror = () => setError("Failed to load Adobe SDK");
      document.body.appendChild(s);
    } else {
      onSdkReady();
    }
    // cleanup not needed; SDK is global
  }, []);

  // When SDK ready, render PDF
  useEffect(() => {
    async function initViewer() {
      if (!adobeReady || !containerRef.current) return;
      if (!ADOBE_KEY) {
        setError("Missing REACT_APP_ADOBE_EMBED_API_KEY");
        return;
      }
      try {
        const view = new window.AdobeDC.View({
          clientId: ADOBE_KEY,
          divId: "adobe-dc-viewer",
        });
        await view.previewFile(
          {
            content: { location: { url: `${apiBase}/files/${encodeURIComponent(fileName)}` } },
            metaData: { fileName },
          },
          { embedMode: "SIZED_CONTAINER", showDownloadPDF: false }
        );

        // Use SELECTION_END + getSelectedContent for robust selection text
        view.registerCallback(
          window.AdobeDC.View.Enum.CallbackType.EVENT_LISTENER,
          async (event) => {
            if (event.type === "SELECTION_END") {
              try {
                const selected = await view.getSelectedContent();
                const text = Array.isArray(selected) && selected[0]?.Text ? selected[0].Text : "";
                if (text && text.trim().length > 5) {
                  await analyze(text);
                }
              } catch (e) {
                console.error("getSelectedContent error", e);
              }
            }
          },
          { enableFilePreviewEvents: true }
        );
      } catch (e) {
        console.error(e);
        setError("Failed to initialize PDF viewer");
      }
    }
    initViewer();
  }, [adobeReady, apiBase, fileName, analyze]);

  async function generatePodcast() {
    if (!result?.podcast_script) return;
    try {
      const { data } = await axios.post(`${apiBase}/generate_podcast`, {
        script: result.podcast_script,
        speaker_mode: "duo",
      });
      setResult((r) => ({ ...r, podcast: data.audio, transcript: data.transcript }));
    } catch (e) {
      console.error(e);
      alert("Podcast generation failed");
    }
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 400px", height: "100vh" }}>
      <div style={{ padding: 12 }}>
        <button onClick={onBack}>← Back</button>
        <div
          id="adobe-dc-viewer"
          ref={containerRef}
          style={{ height: "calc(100vh - 60px)", marginTop: 12, border: "1px solid #ddd" }}
        />
        {error && (
          <div style={{ marginTop: 12, color: "white", background: "#d33", padding: 12 }}>
            PDF Viewer Error<br />
            {error}<br />
            <button onClick={() => window.location.reload()}>Reload Page</button>
          </div>
        )}
      </div>

      {/* Right Panel: Chat + Insights */}
      <div style={{ borderLeft: "1px solid #eee", padding: 12, overflowY: "auto" }}>
        {/* Chat Section */}
        <div style={{ marginBottom: 24, padding: 16, background: "#f8f9fa", borderRadius: 8 }}>
          <h3>💬 Chat with PDF</h3>
          <div style={{ marginBottom: 12 }}>
            <input
              type="text"
              placeholder="Ask a question about this PDF..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              style={{ 
                width: "100%", 
                padding: "8px 12px", 
                border: "1px solid #ddd", 
                borderRadius: 4,
                marginBottom: 8
              }}
              onKeyPress={(e) => e.key === "Enter" && askQuestion()}
            />
            <button 
              onClick={askQuestion} 
              disabled={chatLoading || !question.trim()}
              style={{
                background: "#007bff",
                color: "white",
                border: "none",
                padding: "8px 16px",
                borderRadius: 4,
                cursor: "pointer"
              }}
            >
              {chatLoading ? "Thinking..." : "Ask Question"}
            </button>
          </div>
          
          {chatAnswer && (
            <div style={{ marginTop: 16 }}>
              <h4>🤖 Answer:</h4>
              <div style={{ 
                background: "white", 
                padding: 12, 
                borderRadius: 4, 
                border: "1px solid #ddd",
                marginBottom: 8
              }}>
                {chatAnswer}
              </div>
              
              {audioUrl && (
                <div>
                  <h5>🔊 Audio Answer:</h5>
                  <audio controls src={audioUrl} style={{ width: "100%" }} />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Insights Section */}
        <div style={{ marginBottom: 12 }}>
          <h3>🧠 Text Analysis</h3>
          <label>Paste selection (fallback if text selection isn't detected):</label>
          <textarea
            rows={5}
            value={manualText}
            onChange={(e) => setManualText(e.target.value)}
            style={{ width: "100%" }}
            placeholder="Paste text here, then click Analyze"
          />
          <button disabled={!manualText || loading} onClick={() => analyze(manualText)}>
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>

        {result && (
          <>
            <div>
              <strong>Current PDF:</strong> {result.current_pdf}
              <br />
              <strong>Selected Text:</strong>
              <div style={{ whiteSpace: "pre-wrap", background: "#fafafa", padding: 8, border: "1px solid #eee" }}>
                {result.selected_text}
              </div>
            </div>

            <h4>Relevant Sections Across PDFs</h4>
            <ul>
              {result.related_sections.map((r, i) => (
                <li key={i} style={{ marginBottom: 8 }}>
                  <div><strong>{r.pdf}</strong> — {r.heading}</div>
                  <div>Pages: {r.page_start}-{r.page_end}</div>
                  <div style={{ fontStyle: "italic" }}>{r.snippet}</div>
                </li>
              ))}
            </ul>

            <h4>Insights & Podcast Script</h4>
            <pre style={{ whiteSpace: "pre-wrap", background: "#f6f6f6", padding: 8 }}>
{result.insights_text}
            </pre>

            <button onClick={generatePodcast}>Generate Podcast (Azure TTS)</button>
            {result.podcast && (
              <>
                <h4>Podcast</h4>
                <audio controls src={`${apiBase}${result.podcast}`} />
                <h5>Transcript</h5>
                <pre style={{ whiteSpace: "pre-wrap" }}>{result.transcript}</pre>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
