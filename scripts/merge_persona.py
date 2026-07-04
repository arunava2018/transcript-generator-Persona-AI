import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import MERGE_PERSONA_PROMPT

# ---------------------------------------------------
# Config
# ---------------------------------------------------

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

PERSONA = "hitesh"

MODEL = "gemini-2.5-flash"

INPUT_DIR = Path(f"analysis/intermediate/{PERSONA}")

OUTPUT_DIR = Path(f"analysis/final/{PERSONA}")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------
# Read Intermediate Persona Analysis
# ---------------------------------------------------

files = sorted(INPUT_DIR.glob("batch_*.json"))

print(f"Found {len(files)} batch analysis files.\n")

merged = []

for index, file in enumerate(files, start=1):

    print(f"Reading {file.name}")

    with open(file, "r", encoding="utf-8") as f:

        merged.append({
            "batch": index,
            "source_file": file.name,
            "analysis": json.load(f)
        })

print("\nGenerating Master Persona...\n")

# ---------------------------------------------------
# Prompt
# ---------------------------------------------------

user_prompt = f"""
Below are independent communication analyses of the SAME programming educator.

Each batch was generated from different groups of YouTube transcripts.

Treat every batch as an independent observation.

Use consensus voting while synthesizing the final persona.

Analyses:

{json.dumps(merged, indent=2, ensure_ascii=False)}
"""

# ---------------------------------------------------
# Gemini
# ---------------------------------------------------

response = client.models.generate_content(

    model=MODEL,

    contents=user_prompt,

    config=types.GenerateContentConfig(

        system_instruction=MERGE_PERSONA_PROMPT,

        response_mime_type="application/json",

        temperature=0.1

    )

)

response_text = response.text.strip()

if response_text.startswith("```json"):
    response_text = response_text.replace("```json", "")
    response_text = response_text.replace("```", "").strip()

persona = json.loads(response_text)

# ---------------------------------------------------
# Save
# ---------------------------------------------------

output_file = OUTPUT_DIR / f"{PERSONA}.persona.json"

with open(
    output_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        persona,
        f,
        indent=4,
        ensure_ascii=False
    )

print("\n" + "=" * 80)
print("Master Persona Generated Successfully")
print(f"Saved -> {output_file}")
print("=" * 80)