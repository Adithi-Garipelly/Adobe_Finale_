import { useState, useCallback } from 'react';

export function useInsights() {
  const [insights, setInsights] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateInsights = useCallback(async (selectedText, documentName) => {
    if (!selectedText.trim()) {
      setError('Please provide some text to analyze');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8080/selection/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          selected_text: selectedText,
          current_doc_name: documentName,
          top_k: 5
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.status === 'success') {
        setInsights(data);
        console.log('✅ Insights generated successfully:', data);
      } else {
        throw new Error(data.error || 'Failed to generate insights');
      }
    } catch (err) {
      console.error('❌ Error generating insights:', err);
      setError(err.message);
      
      // Set fallback insights
      setInsights({
        status: 'error',
        selected_text: selectedText,
        related_sections: [],
        insights: `Error occurred while processing your request: ${err.message}`,
        generated_at: new Date().toISOString()
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearInsights = useCallback(() => {
    setInsights(null);
    setError(null);
  }, []);

  const refreshInsights = useCallback(() => {
    if (insights?.selected_text) {
      generateInsights(insights.selected_text, insights.current_doc_name);
    }
  }, [insights, generateInsights]);

  return {
    insights,
    isLoading,
    error,
    generateInsights,
    clearInsights,
    refreshInsights
  };
}
