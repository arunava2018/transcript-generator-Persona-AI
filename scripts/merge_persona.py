import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from prompts import MERGE_PERSONA_PROMPT

# ---------------------------------------------------
# Config
# ---------------------------------------------------

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

PERSONA = "hitesh"

# Examples:
# google/gemini-2.5-flash
# google/gemini-2.5-pro
MODEL = "poolside/laguna-xs-2.1:free"

INPUT_DIR = Path(f"analysis/intermediate/{PERSONA}")
OUTPUT_DIR = Path(f"analysis/final/{PERSONA}")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------
# Read Intermediate Persona Analysis
# ---------------------------------------------------

files = sorted(INPUT_DIR.glob("batch_*.json"))

print(f"Found {len(files)} batch analysis file(s).\n")

merged = []

for index, file in enumerate(files, start=1):

    print(f"Reading {file.name}")

    with open(file, "r", encoding="utf-8") as f:
        merged.append(
            {
                "batch": index,
                "source_file": file.name,
                "analysis": json.load(f),
            }
        )

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
# JSON Parser
# ---------------------------------------------------

def parse_json_response(raw_text: str):
    text = (raw_text or "").strip()

    if not text:
        raise ValueError("The model returned an empty response.")

    cleaned = text

    # Remove markdown code fences
    if cleaned.startswith("```"):
        match = re.match(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.S)
        if match:
            cleaned = match.group(1).strip()

    # Direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Extract first valid JSON object/array
    decoder = json.JSONDecoder()

    for start in ("{", "["):
        idx = cleaned.find(start)

        while idx != -1:
            candidate = cleaned[idx:]

            try:
                parsed, _ = decoder.raw_decode(candidate)
                return parsed
            except json.JSONDecodeError:
                idx = cleaned.find(start, idx + 1)

    raise ValueError(
        f"Could not parse JSON from model response:\n{cleaned[:2000]}"
    )


# ---------------------------------------------------
# OpenRouter Request
# ---------------------------------------------------

response = client.chat.completions.create(
    model=MODEL,
    temperature=0.2,
    response_format={"type": "json_object"},
    messages=[
        {
            "role": "system",
            "content": MERGE_PERSONA_PROMPT,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
    extra_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Persona Analyzer",
    },
)

response_text = (
    response.choices[0].message.content or ""
).strip()

try:
    persona = parse_json_response(response_text)

except (ValueError, json.JSONDecodeError) as exc:

    print("Failed to parse model response as JSON.\n")
    print(response_text[:4000])

    raise SystemExit(exc) from exc


# ---------------------------------------------------
# Save
# ---------------------------------------------------

output_file = OUTPUT_DIR / f"{PERSONA}.persona.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(
        persona,
        f,
        indent=4,
        ensure_ascii=False,
    )

print("\n" + "=" * 80)
print("Master Persona Generated Successfully")
print(f"Saved -> {output_file}")
print("=" * 80)