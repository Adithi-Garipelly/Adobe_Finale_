import os
from typing import List, Dict, Any, Tuple
from .llm_adapter import gemini_complete

_SYSTEM_PROMPT = """You are a helpful research assistant. 
You must stay strictly grounded in the provided material from the user's PDFs.
Output three blocks:
1) "Relevant Sections from Documents" with per-document bullets: (PDF name, page(s), heading, 2–4 sentence snippet).
2) "Overall Insights (Summary & Connections)" with: definitions/overlaps, contradictions/challenges, examples/extensions.
3) "Podcast Transcript" of ~2–3 minutes, 1 or 2 speakers, engaging but factual, grounded only in the provided snippets.
Do NOT add outside sources or claims. If something is missing, say so succinctly.
"""

def generate_insights_from_selection(selection: str, related: List[Dict[str, Any]]):
    # Build grounded context for Gemini
    context_blocks = []
    for r in related:
        ctx = f"""PDF: {r['pdf']}
Heading: {r['heading']}
Pages: {r['page_start']}-{r['page_end']}
Snippet: {r['snippet']}"""
        context_blocks.append(ctx)
    context = "\n\n".join(context_blocks) if context_blocks else "No related sections found."

    user_prompt = f"""User's selected text:
\"\"\"{selection}\"\"\"

Relevant sections (grounding):
{context}

Now produce:
- Relevant Sections from Documents (structured).
- Overall Insights (Summary & Connections).
- Podcast Transcript (approx 2–3 mins, single or dual speaker)."""

    completion = gemini_complete(system_prompt=_SYSTEM_PROMPT, user_prompt=user_prompt)
    # For convenience, re-use the same transcript as the podcast script
    podcast_script = completion
    return completion, podcast_script

def build_insights_payload(current_pdf: str, selection: str, snippets: List[Dict[str, Any]], insights: str, podcast_script: str):
    return {
        "current_pdf": current_pdf,
        "selected_text": selection,
        "related_sections": snippets,
        "insights_text": insights,
        "podcast_script": podcast_script
    }
