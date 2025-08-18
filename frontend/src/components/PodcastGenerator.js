import React, { useState } from "react";
import axios from "axios";

function PodcastGenerator({ insights, apiBase }) {
  const [loading, setLoading] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [error, setError] = useState("");
  const [audioGenerated, setAudioGenerated] = useState(false);
  const [message, setMessage] = useState("");

  const generatePodcast = async () => {
    if (!insights || Object.keys(insights).length === 0) {
      setError("No insights available to generate podcast");
      return;
    }

    setLoading(true);
    setError("");
    setTranscript("");
    setAudioUrl("");
    setAudioGenerated(false);
    setMessage("");

    try {
      const res = await axios.post(`${apiBase}/podcast/generate_podcast`, {
        insights: insights
      });

      if (res.data.status === "success") {
        setTranscript(res.data.transcript);
        setAudioGenerated(res.data.audioGenerated || false);
        
        if (res.data.audioUrl) {
          setAudioUrl(`${apiBase}${res.data.audioUrl}`);
        }
        
        if (res.data.message) {
          setMessage(res.data.message);
        }
        
        setError("");
      } else {
        throw new Error(res.data.error || "Failed to generate podcast");
      }
    } catch (err) {
      console.error("Podcast generation error:", err);
      const errorMessage = err.response?.data?.error || err.message || "Podcast generation failed";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-4 p-4 border rounded-lg shadow bg-white">
      <h3 className="text-lg font-semibold mb-3">🎙️ Enhanced Podcast Generation</h3>
      <p className="text-sm text-gray-600 mb-3">
        Powered by Gemini 2.5 Flash + Azure Neural TTS
      </p>
      
      <button
        onClick={generatePodcast}
        disabled={loading}
        className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
      >
        {loading ? "🎵 Generating with Gemini 2.5..." : "🎙️ Generate Enhanced Podcast"}
      </button>

      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">❌ {error}</p>
        </div>
      )}

      {message && (
        <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-700 text-sm">⚠️ {message}</p>
        </div>
      )}

      {transcript && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-2">📝 Podcast Transcript (Gemini 2.5 Flash)</h4>
          <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
            {transcript}
          </p>
        </div>
      )}

      {audioUrl && audioGenerated && (
        <div className="mt-4 p-3 bg-green-50 rounded-lg">
          <h4 className="font-semibold text-green-800 mb-2">🎵 Podcast Audio (Azure Neural TTS)</h4>
          <audio 
            controls 
            src={audioUrl} 
            className="mt-2 w-full rounded-lg"
            preload="metadata"
          />
          <p className="text-xs text-green-600 mt-2">
            🎯 High-quality audio generated with Azure Neural TTS (Jenny Neural Voice)
          </p>
        </div>
      )}

      {!audioGenerated && transcript && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <h4 className="font-semibold text-blue-800 mb-2">🎯 Audio Status</h4>
          <p className="text-sm text-blue-700">
            Transcript generated successfully! Audio generation requires valid Azure TTS credentials.
          </p>
        </div>
      )}

      <div className="mt-3 text-xs text-gray-500">
        <p>✨ Gemini 2.5 Flash: Advanced AI for natural transcript generation</p>
        <p>🎯 Azure Neural TTS: Professional-grade audio quality</p>
        <p>🚀 Region: Central India (optimized for your location)</p>
      </div>
    </div>
  );
}

export default PodcastGenerator;
