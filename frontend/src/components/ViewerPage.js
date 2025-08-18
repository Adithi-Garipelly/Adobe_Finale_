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

  // Parse structured insights
  const parseInsights = (insightsText) => {
    const sections = {
      definitions: "",
      contradictions: "",
      examples: "",
      evolution: "",
      synthesis: ""
    };
    
    const lines = insightsText.split('\n');
    let currentSection = "";
    
    for (const line of lines) {
      if (line.includes('DEFINITIONS & CORE CONCEPTS')) {
        currentSection = "definitions";
      } else if (line.includes('CONTRADICTORY FINDINGS & CHALLENGES')) {
        currentSection = "contradictions";
      } else if (line.includes('EXAMPLES & APPLICATIONS')) {
        currentSection = "examples";
      } else if (line.includes('EVOLUTION & EXTENSIONS')) {
        currentSection = "evolution";
      } else if (line.includes('SYNTHESIS & CONNECTIONS')) {
        currentSection = "synthesis";
      } else if (currentSection && line.trim()) {
        sections[currentSection] += line + '\n';
      }
    }
    
    return sections;
  };

  const insights = result ? parseInsights(result.insights_text) : null;

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 450px", height: "100vh" }}>
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

      {/* Right Panel: Chat + Research Insights */}
      <div style={{ borderLeft: "1px solid #eee", padding: 12, overflowY: "auto" }}>
        {/* Chat Section */}
        <div style={{ marginBottom: 24, padding: 16, background: "#f8f9fa", borderRadius: 8 }}>
          <h3>💬 Quick Question</h3>
          <div style={{ marginBottom: 12 }}>
            <input
              type="text"
              placeholder="Ask a quick question about this PDF..."
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
              {chatLoading ? "Thinking..." : "Ask"}
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
                  <h5>🔊 Audio:</h5>
                  <audio controls src={audioUrl} style={{ width: "100%" }} />
                </div>
              )}
            </div>
          )}
        </div>

        {/* Research Insights Section */}
        <div style={{ marginBottom: 12 }}>
          <h3>🧠 Research Insights</h3>
          <p style={{ fontSize: "14px", color: "#666", marginBottom: 16 }}>
            Select text in the PDF to analyze across your entire document library
          </p>
          
          <label>Manual Text Input (if selection doesn't work):</label>
          <textarea
            rows={4}
            value={manualText}
            onChange={(e) => setManualText(e.target.value)}
            style={{ width: "100%", marginBottom: 8 }}
            placeholder="Paste text here, then click Analyze"
          />
          <button disabled={!manualText || loading} onClick={() => analyze(manualText)}>
            {loading ? "Analyzing..." : "Analyze Text"}
          </button>
        </div>

        {/* Structured Insights Display */}
        {result && insights && (
          <div style={{ marginTop: 20 }}>
            <div style={{ marginBottom: 16 }}>
              <strong>📄 Current PDF:</strong> {result.current_pdf}
              <br />
              <strong>🔍 Selected Text:</strong>
              <div style={{ 
                whiteSpace: "pre-wrap", 
                background: "#f8f9fa", 
                padding: 8, 
                border: "1px solid #eee",
                fontSize: "13px",
                maxHeight: "100px",
                overflowY: "auto"
              }}>
                {result.selected_text}
              </div>
            </div>

            {/* Analysis Metadata */}
            {result.analysis_metadata && (
              <div style={{ 
                background: "#e3f2fd", 
                padding: 12, 
                borderRadius: 6, 
                marginBottom: 16,
                fontSize: "13px"
              }}>
                <strong>📊 Analysis Summary:</strong><br/>
                • Documents analyzed: {result.analysis_metadata.total_documents_analyzed}<br/>
                • Search scope: {result.analysis_metadata.search_scope}<br/>
                • Grounding: {result.analysis_metadata.grounding}
              </div>
            )}

            {/* Related Sections */}
            <h4>📚 Related Sections Across Documents</h4>
            <div style={{ maxHeight: "200px", overflowY: "auto", marginBottom: 16 }}>
              {result.related_sections.map((r, i) => (
                <div key={i} style={{ 
                  background: "#f8f9fa", 
                  padding: 8, 
                  marginBottom: 8, 
                  borderRadius: 4,
                  borderLeft: "3px solid #007bff"
                }}>
                  <div><strong>{r.pdf}</strong> — {r.heading}</div>
                  <div style={{ fontSize: "12px", color: "#666" }}>Pages: {r.page_start}-{r.page_end}</div>
                  <div style={{ fontStyle: "italic", fontSize: "13px" }}>{r.snippet}</div>
                </div>
              ))}
            </div>

            {/* Structured Insights */}
            <h4>🔍 Cross-Document Insights</h4>
            
            {insights.definitions && (
              <div style={{ marginBottom: 16 }}>
                <h5 style={{ color: "#2e7d32", marginBottom: 8 }}>📖 Definitions & Core Concepts</h5>
                <div style={{ 
                  background: "#f1f8e9", 
                  padding: 12, 
                  borderRadius: 4,
                  fontSize: "13px",
                  whiteSpace: "pre-wrap"
                }}>
                  {insights.definitions.trim()}
                </div>
              </div>
            )}

            {insights.contradictions && (
              <div style={{ marginBottom: 16 }}>
                <h5 style={{ color: "#d32f2f", marginBottom: 8 }}>⚠️ Contradictions & Challenges</h5>
                <div style={{ 
                  background: "#ffebee", 
                  padding: 12, 
                  borderRadius: 4,
                  fontSize: "13px",
                  whiteSpace: "pre-wrap"
                }}>
                  {insights.contradictions.trim()}
                </div>
              </div>
            )}

            {insights.examples && (
              <div style={{ marginBottom: 16 }}>
                <h5 style={{ color: "#1976d2", marginBottom: 8 }}>💡 Examples & Applications</h5>
                <div style={{ 
                  background: "#e3f2fd", 
                  padding: 12, 
                  borderRadius: 4,
                  fontSize: "13px",
                  whiteSpace: "pre-wrap"
                }}>
                  {insights.examples.trim()}
                </div>
              </div>
            )}

            {insights.evolution && (
              <div style={{ marginBottom: 16 }}>
                <h5 style={{ color: "#7b1fa2", marginBottom: 8 }}>🚀 Evolution & Extensions</h5>
                <div style={{ 
                  background: "#f3e5f5", 
                  padding: 12, 
                  borderRadius: 4,
                  fontSize: "13px",
                  whiteSpace: "pre-wrap"
                }}>
                  {insights.evolution.trim()}
                </div>
              </div>
            )}

            {insights.synthesis && (
              <div style={{ marginBottom: 16 }}>
                <h5 style={{ color: "#f57c00", marginBottom: 8 }}>🔗 Synthesis & Connections</h5>
                <div style={{ 
                  background: "#fff3e0", 
                  padding: 12, 
                  borderRadius: 4,
                  fontSize: "13px",
                  whiteSpace: "pre-wrap"
                }}>
                  {insights.synthesis.trim()}
                </div>
              </div>
            )}

            {/* Podcast Generation */}
            <div style={{ marginTop: 20, padding: 16, background: "#f8f9fa", borderRadius: 8 }}>
              <h4>🎙️ Generate Research Podcast</h4>
              <p style={{ fontSize: "13px", color: "#666", marginBottom: 12 }}>
                Convert insights into an engaging audio summary
              </p>
              <button 
                onClick={generatePodcast}
                style={{
                  background: "#28a745",
                  color: "white",
                  border: "none",
                  padding: "10px 20px",
                  borderRadius: 4,
                  cursor: "pointer"
                }}
              >
                🎙️ Create Podcast
              </button>
              
              {result.podcast && (
                <div style={{ marginTop: 16 }}>
                  <h5>🎧 Your Research Podcast:</h5>
                  <audio controls src={`${apiBase}${result.podcast}`} style={{ width: "100%" }} />
                  <h6>📝 Transcript:</h6>
                  <div style={{ 
                    background: "white", 
                    padding: 12, 
                    borderRadius: 4, 
                    border: "1px solid #ddd",
                    fontSize: "12px",
                    maxHeight: "150px",
                    overflowY: "auto",
                    whiteSpace: "pre-wrap"
                  }}>
                    {result.transcript}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
