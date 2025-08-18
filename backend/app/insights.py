import os
from typing import List, Dict, Any, Tuple
from .llm_adapter import gemini_complete

_SYSTEM_PROMPT = """You are an expert research analyst creating contextual insights across multiple PDF documents.

Your task is to analyze selected text and find connections, contradictions, and extensions across the document library.

Generate insights in this EXACT structure:

1. DEFINITIONS & CORE CONCEPTS
- Surface key definitions from relevant documents
- Identify overlapping explanations
- Note any conceptual evolution

2. CONTRADICTORY FINDINGS & CHALLENGES
- Highlight conflicting perspectives
- Identify negative transfer or limitations
- Note methodological disagreements

3. EXAMPLES & APPLICATIONS
- Find practical examples across documents
- Identify use cases and implementations
- Note domain-specific applications

4. EVOLUTION & EXTENSIONS
- Track concept development over time
- Identify emerging trends or extensions
- Note future research directions

5. SYNTHESIS & CONNECTIONS
- Summarize key insights
- Connect findings across documents
- Highlight research gaps

IMPORTANT RULES:
- Base ALL insights ONLY on the provided document snippets
- Do NOT add external knowledge or web information
- If something is missing, say "Not found in current documents"
- Be specific and reference document names when possible
- Focus on academic/research quality insights
- Keep each section concise but comprehensive
"""

def generate_insights_from_selection(selection: str, related: List[Dict[str, Any]]):
    # Build grounded context for Gemini
    context_blocks = []
    for r in related:
        ctx = f"""DOCUMENT: {r['pdf']}
HEADING: {r['heading']}
PAGES: {r['page_start']}-{r['page_end']}
CONTENT: {r['snippet']}"""
        context_blocks.append(ctx)
    
    context = "\n\n".join(context_blocks) if context_blocks else "No related sections found in current documents."

    user_prompt = f"""SELECTED TEXT:
\"\"\"{selection}\"\"\"

RELEVANT DOCUMENT SECTIONS (from your library):
{context}

ANALYSIS TASK:
Analyze the selected text in context of your entire PDF library. Find connections, contradictions, and extensions across documents.

Generate insights that help researchers understand:
- How this concept is defined across different sources
- Where perspectives conflict or complement each other
- How the concept has evolved or been extended
- What examples and applications exist
- How to synthesize findings across documents

Focus on academic quality and research insights."""

    completion = gemini_complete(system_prompt=_SYSTEM_PROMPT, user_prompt=user_prompt)
    
    # Generate podcast script from insights
    podcast_script = _create_podcast_script(selection, completion, related)
    
    return completion, podcast_script

def _create_podcast_script(selection: str, insights: str, related: List[Dict[str, Any]]) -> str:
    """Create an engaging podcast script from the insights"""
    
    podcast_prompt = f"""Create an engaging 2-3 minute podcast script from these research insights.

SELECTED TEXT: {selection}

INSIGHTS: {insights}

REQUIREMENTS:
- Format as a conversation between Host and Co-host
- Make it engaging and educational
- Structure: Intro → Key Findings → Contradictions → Examples → Summary
- Use natural, conversational language
- Include specific document references when relevant
- End with actionable insights for researchers

OUTPUT FORMAT:
Host: [Introduction and context]
Co-host: [Key findings and definitions]
Host: [Contradictions and challenges]
Co-host: [Examples and applications]
Host: [Evolution and extensions]
Co-host: [Synthesis and summary]
Host: [Closing thoughts and next steps]"""

    try:
        return gemini_complete(
            system_prompt="You are a podcast script writer creating engaging research content.",
            user_prompt=podcast_prompt
        )
    except:
        # Fallback script if Gemini fails
        return f"""Host: Welcome to Research Insights! Today we're exploring the concept from your selected text.

Co-host: Based on your document library, we found some fascinating connections across multiple research papers.

Host: Let's dive into the key findings and see how different sources define and approach this concept.

Co-host: We'll also explore any contradictions, examples, and how the concept has evolved over time.

Host: Stay tuned for actionable insights that could shape your research direction!"""

def build_insights_payload(current_pdf: str, selection: str, snippets: List[Dict[str, Any]], insights: str, podcast_script: str):
    return {
        "current_pdf": current_pdf,
        "selected_text": selection,
        "related_sections": snippets,
        "insights_text": insights,
        "podcast_script": podcast_script,
        "analysis_metadata": {
            "total_documents_analyzed": len(set(s['pdf'] for s in snippets)),
            "insight_categories": [
                "Definitions & Core Concepts",
                "Contradictory Findings & Challenges", 
                "Examples & Applications",
                "Evolution & Extensions",
                "Synthesis & Connections"
            ],
            "search_scope": "Full document library",
            "grounding": "Uploaded PDFs only"
        }
    }
