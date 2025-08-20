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
    
    podcast_prompt = f"""Create an engaging, interactive 3-5 minute research podcast transcript from these insights.

SELECTED TEXT: {selection}

INSIGHTS: {insights}

REQUIREMENTS:
- Create a natural, conversational two-person podcast dialogue
- Make it engaging, educational, and smooth-flowing
- Structure: 
  * Hook & Introduction (30 seconds)
  * Key Findings & Definitions (1-1.5 minutes)
  * Contradictions & Challenges (1-1.5 minutes)
  * Examples & Applications (1-1.5 minutes)
  * Synthesis & Future Directions (30 seconds)
- Use natural, conversational language with research enthusiasm
- Include specific document references when relevant
- Add engaging transitions and questions between speakers
- End with actionable insights and next steps for researchers
- Make it sound like a professional research podcast
- Ensure smooth conversation flow without abrupt transitions
- If content is too short, expand conversation naturally (but don't add new technical content)

OUTPUT FORMAT:
Create a natural conversation flow between two hosts discussing the research. Use simple speaker labels like "Sarah:" and "Alex:" without stage directions or formatting markers. Make it sound like a real podcast conversation.

CRITICAL: DO NOT include any stage directions like "(Intro Music fades in and out)", "(Outro Music fades in)", or any text in parentheses. Only include the actual spoken conversation between Sarah and Alex."""

    try:
        return gemini_complete(
            system_prompt="You are an expert podcast transcript writer specializing in academic research content. Create natural, conversational transcripts that make complex research accessible and exciting. Focus on smooth dialogue flow, remove stage directions, use simple speaker labels (Sarah: and Alex:), and ensure the conversation sounds like a real podcast. Keep it engaging and conversational without being overly formal.",
            user_prompt=podcast_prompt
        )
    except:
        # Enhanced fallback script if Gemini fails
        return f"""Sarah: Welcome to Research Insights, where we dive deep into the latest academic discoveries! I'm Sarah, and today we're exploring a fascinating concept from your research.

Alex: Hi everyone! I'm Alex, and I'm excited to break down this concept across multiple research papers. What we found is absolutely fascinating!

Sarah: Absolutely! So, we're looking at the concept from your selected text, and Alex, what are the key findings across these documents?

Alex: Great question! Based on your document library, we've discovered some incredible connections. The concept appears in multiple contexts, each adding a unique perspective to our understanding.

Sarah: That's intriguing! And what about contradictions or challenges? Research isn't always straightforward, right?

Alex: Exactly! We found some fascinating contradictions that actually highlight important research gaps. Different methodologies and contexts lead to varying conclusions.

Sarah: Perfect! Now let's talk examples and applications. What practical insights can researchers take away?

Alex: Excellent point! We identified several concrete examples and use cases that demonstrate how this concept works in practice.

Sarah: And what about the future? Where is this research heading?

Alex: That's the exciting part! We're seeing emerging trends and new applications that suggest this field is evolving rapidly.

Sarah: Amazing! So what should researchers do next? What are our actionable takeaways?

Alex: Great question! Based on our analysis, researchers should focus on bridging the gaps we identified and exploring the emerging applications we discovered.

Sarah: Perfect! This has been an incredible deep-dive into cross-document research insights. Thanks for joining us, and happy researching!"""

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
