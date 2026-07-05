import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from prompts import BATCH_ANALYSIS_PROMPT

# ---------------------------------------------------
# Config
# ---------------------------------------------------

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

PERSONA = "hitesh"

BATCH_SIZE = 3

# Examples:
# "google/gemini-2.5-pro"
# "google/gemini-2.5-flash"
# "google/gemini-2.0-flash-001"

MODEL = "poolside/laguna-xs-2.1:free"

TRANSCRIPT_DIR = Path(f"transcripts/{PERSONA}")
OUTPUT_DIR = Path(f"analysis/intermediate/{PERSONA}")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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
# Read transcript files
# ---------------------------------------------------

files = sorted(TRANSCRIPT_DIR.glob("*.txt"))

print(f"Found {len(files)} transcript(s)")


# ---------------------------------------------------
# Create batches
# ---------------------------------------------------

batches = [
    files[i:i + BATCH_SIZE]
    for i in range(0, len(files), BATCH_SIZE)
]

print(f"Created {len(batches)} batch(es)\n")


# ---------------------------------------------------
# Process each batch
# ---------------------------------------------------

for batch_index, batch in enumerate(batches, start=1):

    print("=" * 80)
    print(f"Processing Batch {batch_index}")
    print("=" * 80)

    merged_transcript = ""

    for file in batch:

        print(f"Reading {file.name}")

        with open(file, "r", encoding="utf-8") as f:
            transcript = f.read()

        merged_transcript += f"""

====================================================
VIDEO : {file.stem}
====================================================

{transcript}

"""

    user_prompt = f"""
The following transcripts belong to the SAME educator.

Analyze ONLY the educator's communication style, teaching style,
personality, vocabulary, recurring phrases, tone, and behavioral patterns.

Ignore the programming concepts completely.

Transcripts:

{merged_transcript}
"""

    print("Sending request to OpenRouter...\n")

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": BATCH_ANALYSIS_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        response_format={
            "type": "json_object"
        },
        extra_headers={
            # Optional but recommended by OpenRouter
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Persona Analyzer",
        },
    )

    response_text = (
        response.choices[0].message.content or ""
    ).strip()

    try:
        persona_json = parse_json_response(response_text)

    except (ValueError, json.JSONDecodeError) as exc:

        print("Failed to parse JSON response.\n")
        print(response_text[:4000])

        raise SystemExit(exc) from exc

    output_file = OUTPUT_DIR / f"batch_{batch_index}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            persona_json,
            f,
            indent=4,
            ensure_ascii=False,
        )

    print(f"Saved -> {output_file}\n")


print("=" * 80)
print("Finished Successfully")
print("=" * 80)