import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from prompts import FEW_SHOTS_PROMPT

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
    temperature=0.8,
    response_format={"type": "json_object"},
    messages=[
        {
            "role": "system",
            "content": FEW_SHOTS_PROMPT,
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
    fewshots = parse_json_response(response_text)

except (ValueError, json.JSONDecodeError) as exc:

    print("Failed to parse model response as JSON.\n")
    print(response_text[:4000])

    raise SystemExit(exc) from exc

# ---------------------------------------------------
# Save
# ---------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        fewshots,
        f,
        indent=4,
        ensure_ascii=False,
    )

print("=" * 80)
print("Few-shot Examples Generated Successfully")
print(f"Saved -> {OUTPUT_FILE}")
print("=" * 80)