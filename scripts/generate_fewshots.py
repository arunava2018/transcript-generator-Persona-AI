import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import FEW_SHOTS_PROMPT

# ---------------------------------------------------
# Config
# ---------------------------------------------------

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

PERSONA = "hitesh"

MODEL = "gemini-3.5-flash"
INPUT_FILE = Path(f"analysis/final/{PERSONA}/{PERSONA}.persona.json")

OUTPUT_FILE = Path(f"analysis/final/{PERSONA}/{PERSONA}.fewshots.json")

# ---------------------------------------------------
# Read Persona
# ---------------------------------------------------

print("Loading Persona...\n")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    persona = json.load(f)

print("Generating Few-shot Examples...\n")

# ---------------------------------------------------
# Prompt
# ---------------------------------------------------

user_prompt = f"""
Below is the final synthesized communication persona.

Generate realistic few-shot conversations.

Persona:

{json.dumps(persona, indent=2, ensure_ascii=False)}
"""

# ---------------------------------------------------
# Gemini
# ---------------------------------------------------

response = client.models.generate_content(

    model=MODEL,

    contents=user_prompt,

    config=types.GenerateContentConfig(

        system_instruction=FEW_SHOTS_PROMPT,

        response_mime_type="application/json",

        temperature=0.8

    )

)

response_text = response.text.strip()

if response_text.startswith("```json"):
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "").strip()

fewshots = json.loads(response_text)

# ---------------------------------------------------
# Save
# ---------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        fewshots,
        f,
        indent=4,
        ensure_ascii=False
    )

print("=" * 80)
print("Few-shot Examples Generated Successfully")
print(f"Saved -> {OUTPUT_FILE}")
print("=" * 80)