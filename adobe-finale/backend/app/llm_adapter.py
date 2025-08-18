# backend/app/llm_adapter.py
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configuration
USE_LLM = os.environ.get("LLM_PROVIDER", "").strip() != ""
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini").lower()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

def _fallback_insights(selected_text: str, related: List[Dict[str, Any]]) -> str:
    """Generate fallback insights when LLM is not available"""
    try:
        if not related:
            return """Definition & Core Principle: The selected text appears to be a unique concept in your library with no direct matches in other documents.

Application & Context: This concept may be specific to the document you're analyzing, requiring further research or additional documents for broader context.

Contradictory Viewpoints / Challenges: No contrasting perspectives found in your current library. Consider uploading more diverse documents to identify potential challenges or alternative viewpoints.

Model Comparison: Unable to compare approaches without related sections. The selected text represents a standalone concept in your current document collection.

Extension to Other Fields: No extensions identified in your current library. This concept may be domain-specific or require additional research papers to explore broader applications.

Note: Enable LLM_PROVIDER for AI-powered insights generation."""
        
        # Generate structured fallback insights
        docs = {r['doc_name'] for r in related}
        headings = [r['heading'] for r in related]
        high_scores = [r for r in related if r.get('score', 0) > 0.8]
        
        return f"""Definition & Core Principle: Found {len(related)} related sections across your library that connect to the selected text, showing this concept has broader applications and definitions.

Application & Context: The concept appears in {len(docs)} different documents, indicating it's applied across multiple domains and research areas.

Contradictory Viewpoints / Challenges: Results span multiple documents, suggesting complementary or contrasting viewpoints that enrich understanding of the concept.

Model Comparison: Related sections include various approaches and methodologies, providing a comprehensive view of different implementations and models.

Extension to Other Fields: The concept extends beyond the selected text to other research areas, showing its versatility and broader applicability.

Note: Enable LLM_PROVIDER for AI-powered insights generation with deeper analysis."""
        
    except Exception as e:
        logger.error(f"Error generating fallback insights: {e}")
        return """Definition & Core Principle: Error occurred while analyzing the selected text.

Application & Context: Unable to process the selection due to a system error.

Contradictory Viewpoints / Challenges: No analysis available due to technical issues.

Model Comparison: Comparison not possible due to system error.

Extension to Other Fields: Unable to identify extensions due to processing error.

Note: Please try again or contact support if the issue persists."""

def build_prompt(selected_text: str, related: List[Dict[str, Any]]) -> str:
    """Build comprehensive prompt for LLM analysis"""
    try:
        # Prepare context with better formatting
        context = []
        for i, r in enumerate(related, 1):
            context.append(f"[Section {i}] {r['doc_name']} — {r['heading']}\nSnippet: {r['snippet']}\n")
        
        ctx = "\n".join(context)
        
        # Enhanced prompt for EXACT structured format
        return f"""You are an expert research analyst generating insights grounded ONLY in the provided sections (no external knowledge).

SELECTED TEXT:
\"\"\"{selected_text}\"\"\"

RELEVANT SECTIONS (snippets from user's PDF library):
{ctx}

TASKS:
1) Analyze how the selected text connects to the broader research landscape
2) Identify overlaps, contrasts, and extensions across documents
3) Generate structured insights in the EXACT format specified below

OUTPUT FORMAT (MUST FOLLOW THIS EXACT STRUCTURE):

Definition & Core Principle: [Summarize the core concept from the selected text and how it's defined across documents]

Application & Context: [Explain how the concept is applied in the selected text and related documents]

Contradictory Viewpoints / Challenges: [Identify any contradictions, challenges, or different perspectives across documents]

Model Comparison: [Compare different approaches, models, or methods mentioned across documents]

Extension to Other Fields: [Show how the concept extends to other areas or applications]

IMPORTANT REQUIREMENTS:
- Use ONLY the provided sections as context
- Be specific and reference content from the documents
- Connect insights across multiple documents
- Highlight both agreements and disagreements
- Use clear, academic language
- Keep each section concise but comprehensive
- Focus on the selected text as the central theme
- MUST follow the exact format above with the exact headers

Generate insights that would help a researcher understand the broader context and implications of their selected text."""
        
    except Exception as e:
        logger.error(f"Error building prompt: {e}")
        return f"Analyze this text: {selected_text}"

def generate_insights(selected_text: str, related: List[Dict[str, Any]]) -> str:
    """Generate insights using configured LLM or fallback"""
    try:
        if not USE_LLM:
            logger.info("LLM not configured, using fallback insights")
            return _fallback_insights(selected_text, related)
        
        logger.info(f"Generating insights using {LLM_PROVIDER}")
        
        if LLM_PROVIDER == "gemini":
            return _generate_gemini_insights(selected_text, related)
        elif LLM_PROVIDER == "openai":
            return _generate_openai_insights(selected_text, related)
        else:
            logger.warning(f"Unknown LLM provider: {LLM_PROVIDER}, using fallback")
            return _fallback_insights(selected_text, related)
            
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return _fallback_insights(selected_text, related)

def _generate_gemini_insights(selected_text: str, related: List[Dict[str, Any]]) -> str:
    """Generate insights using Google Gemini"""
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not set, using fallback")
            return _fallback_insights(selected_text, related)
        
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Build prompt
        prompt = build_prompt(selected_text, related)
        
        # Generate content
        response = model.generate_content(prompt)
        
        if response and response.text:
            logger.info("✅ Gemini insights generated successfully")
            return response.text.strip()
        else:
            logger.warning("Gemini returned empty response, using fallback")
            return _fallback_insights(selected_text, related)
            
    except ImportError:
        logger.error("google-generativeai not installed")
        return _fallback_insights(selected_text, related)
    except Exception as e:
        logger.error(f"Error generating Gemini insights: {e}")
        return _fallback_insights(selected_text, related)

def _generate_openai_insights(selected_text: str, related: List[Dict[str, Any]]) -> str:
    """Generate insights using OpenAI"""
    try:
        from openai import OpenAI
        
        # Configure OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set, using fallback")
            return _fallback_insights(selected_text, related)
        
        client = OpenAI(api_key=api_key)
        
        # Build prompt
        prompt = build_prompt(selected_text, related)
        
        # Generate completion
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800,
            timeout=30
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            if content:
                logger.info("✅ OpenAI insights generated successfully")
                return content.strip()
        
        logger.warning("OpenAI returned empty response, using fallback")
        return _fallback_insights(selected_text, related)
        
    except ImportError:
        logger.error("openai not installed")
        return _fallback_insights(selected_text, related)
    except Exception as e:
        logger.error(f"Error generating OpenAI insights: {e}")
        return _fallback_insights(selected_text, related)

def get_llm_status() -> Dict[str, Any]:
    """Get LLM configuration status"""
    try:
        status = {
            "enabled": USE_LLM,
            "provider": LLM_PROVIDER if USE_LLM else "none",
            "models": {}
        }
        
        if LLM_PROVIDER == "gemini":
            status["models"]["gemini"] = GEMINI_MODEL
            status["configured"] = bool(os.environ.get("GEMINI_API_KEY"))
        elif LLM_PROVIDER == "openai":
            status["models"]["openai"] = OPENAI_MODEL
            status["configured"] = bool(os.environ.get("OPENAI_API_KEY"))
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting LLM status: {e}")
        return {"error": str(e)}
