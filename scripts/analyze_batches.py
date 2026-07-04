import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from prompts import BATCH_ANALYSIS_PROMPT

# ---------------------------------------------------
# Config
# ---------------------------------------------------

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

PERSONA = "hitesh"

BATCH_SIZE = 4

MODEL = "gemini-2.5-flash"

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

    # Remove markdown code fences if present
    if cleaned.startswith("```"):
        fence_match = re.match(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.S)
        if fence_match:
            cleaned = fence_match.group(1).strip()

    # Try parsing directly
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try extracting the first valid JSON object/array
    decoder = json.JSONDecoder()

    for start in ("{", "["):
        start_idx = cleaned.find(start)

        while start_idx != -1:
            candidate = cleaned[start_idx:]

            try:
                parsed, _ = decoder.raw_decode(candidate)
                return parsed
            except json.JSONDecodeError:
                start_idx = cleaned.find(start, start_idx + 1)

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

Analyze ONLY the educator's communication style and recurring phrases.

Ignore the programming concepts.

Transcripts:

{merged_transcript}
"""

    print("Sending request to Gemini...\n")

    response = client.models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config={
            "system_instruction": BATCH_ANALYSIS_PROMPT,
            "temperature": 0.2,
            "response_mime_type": "application/json",
        },
    )

    response_text = (response.text or "").strip()

    try:
        persona_json = parse_json_response(response_text)
    except (ValueError, json.JSONDecodeError) as exc:
        print("Failed to parse JSON response.")
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