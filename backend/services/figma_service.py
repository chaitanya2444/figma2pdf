# backend/services/figma_service.py
import os
import json
from openai import OpenAI

# Put your OpenRouter key here (free) — or set it as environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

def parse_figma_with_llm(figma_link: str) -> dict:
    """
    Sends the Figma link to a free model on OpenRouter
    Returns clean JSON exactly like before (so PDF generation works unchanged)
    """
    prompt = f"""
You are a senior UI/UX architect. Analyze this Figma design and extract everything needed for a professional system architecture PDF.

Figma link: {figma_link}

Return ONLY valid JSON in this exact structure (no extra text, no markdown):

{{
  "project_name": "Extract project name from title or frames",
  "overview": "2-3 sentence summary of the product",
  "pages": [
    {{
      "name": "Page name",
      "key_frames": [
        {{
          "name": "Frame name",
          "type": "FRAME | COMPONENT | INSTANCE | TEXT | etc",
          "width": 375.0,
          "height": 812.0
        }}
      ]
    }}
  ],
  "ui_elements": [
    {{
      "id": "REQ-001",
      "name": "Button / Input / Card name",
      "type": "BUTTON | TEXT | RECTANGLE | etc",
      "properties": {{}}
    }}
  ],
  "reusable_components": ["Button Primary", "Card User", "Modal Sheet"],
  "design_system": {{
    "colors": {{"primary": "#0066FF", "background": "#FFFFFF"}},
    "typography": [
      {{"name": "Heading", "font_size": 24, "font_family": "Inter"}}
    ]
  }},
  "main_user_flows": [
    "User opens app → sees home screen → taps button → sees modal"
  ],
  "tech_recommendations": "React Native + Tailwind / SwiftUI / Flutter",
  "architecture_notes": "Use component variants, auto-layout, design tokens"
}}

Be extremely accurate. Use the best free model available.
"""

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct:free",           # 100% free & excellent at JSON
        # model="mistralai/mistral-7b-instruct:free",     # also free option
        # model="meta-llama/llama-3.2-3b-instruct:free",  # another free option
        messages=[{"role": "user", "content": prompt}],
        max_tokens=8000,
        temperature=0.1
    )

    raw_text = response.choices[0].message.content.strip()
    
    # Safety: in case model adds markdown
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    
    return json.loads(raw_text)