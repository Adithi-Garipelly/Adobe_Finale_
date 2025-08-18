import React, { useState } from "react";
import axios from "axios";

function PodcastGenerator({ insights, apiBase }) {
  const [loading, setLoading] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [audioUrl, setAudioUrl] = useState("");

  const generatePodcast = async () => {
    if (!insights || Object.keys(insights).length === 0) {
      alert("No insights available to generate podcast");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post(`${apiBase}/podcast/generate_podcast`, {
        insights: insights
      });

      if (res.data.status === "success") {
        setTranscript(res.data.transcript);
        setAudioUrl(`${apiBase}${res.data.audioUrl}`);
      } else {
        throw new Error("Failed to generate podcast");
      }
    } catch (err) {
      console.error(err);
      alert("Podcast generation failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-4 p-4 border rounded-lg shadow bg-white">
      <h3 className="text-lg font-semibold mb-3">🎙️ Enhanced Podcast Generation</h3>
      
      <button
        onClick={generatePodcast}
        disabled={loading}
        className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
      >
        {loading ? "🎵 Generating..." : "🎙️ Generate Enhanced Podcast"}
      </button>

      {transcript && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-2">📝 Podcast Transcript</h4>
          <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
            {transcript}
          </p>
        </div>
      )}

      {audioUrl && (
        <div className="mt-4 p-3 bg-green-50 rounded-lg">
          <h4 className="font-semibold text-green-800 mb-2">🎵 Podcast Audio</h4>
          <audio 
            controls 
            src={audioUrl} 
            className="mt-2 w-full rounded-lg"
            preload="metadata"
          />
          <p className="text-xs text-green-600 mt-2">
            Audio generated with Azure Neural TTS for professional quality
          </p>
        </div>
      )}

      <div className="mt-3 text-xs text-gray-500">
        <p>✨ This enhanced podcast uses Gemini 2.5 Flash for natural transcript generation</p>
        <p>🎯 Audio quality optimized for research and educational content</p>
      </div>
    </div>
  );
}

export default PodcastGenerator;
