import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from prompts import BATCH_ANALYSIS_PROMPT

# ---------------------------------------------------
# Config
# ---------------------------------------------------

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GROQ_API_KEY")
)

PERSONA = "piyush"

BATCH_SIZE = 4

MODEL = "llama-3.3-70b-versatile"

TRANSCRIPT_DIR = Path(f"transcripts/{PERSONA}")

OUTPUT_DIR = Path(f"analysis/intermediate/{PERSONA}")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

    prompt = f"""
{BATCH_ANALYSIS_PROMPT}

----------------------------------------------------

The following transcripts belong to the SAME educator.

Analyze ONLY the educator's communication style.

Ignore the programming concepts.

Transcripts:

{merged_transcript}
"""

    print("Sending request to Gemini...\n")

    response = client.chat.completions.create(
        model=MODEL,
        contents=prompt,
    )
    print(response.text)

    # Gemini sometimes wraps JSON in ```json blocks
    response_text = response.text.strip()

    if response_text.startswith("```json"):
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```", "").strip()

    persona_json = json.loads(response_text)

    output_file = OUTPUT_DIR / f"batch_{batch_index}.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            persona_json,
            f,
            indent=4,
            ensure_ascii=False,
        )

    print(f"Saved -> {output_file}\n")

print("Finished Successfully")