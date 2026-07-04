import os
from youtube_transcript_api import YouTubeTranscriptApi

# ---------------------------------------
# CONFIG
# ---------------------------------------

PERSONA = "piyush"

VIDEO_IDS = [
    "p8ngBrlr9nY",
    "nomgFESEYZI",
    "qhsVMiBjxM0",
    "K45s2PgywvI",
    "f3zHina9MTo",
    "6gBJ5jAIdQI",
    "SI7gdRQcGSY",
    "kRR1K3q5nlg",
    "Y4lpmVymXD4",
    "TcQtqzDtP5A",
    "nm9TCcgE4cQ"
    # Add more ids here
]

LANGUAGES = ["hi", "en"]

OUTPUT_DIR = f"transcripts/{PERSONA}"

os.makedirs(OUTPUT_DIR, exist_ok=True)

ytt = YouTubeTranscriptApi()

# ---------------------------------------
# Download
# ---------------------------------------

for video_id in VIDEO_IDS:

    try:

        print(f"Downloading {video_id}")

        transcript = ytt.fetch(
            video_id,
            languages=LANGUAGES
        )

        text = "\n".join(
            snippet.text
            for snippet in transcript
        )

        file_path = os.path.join(
            OUTPUT_DIR,
            f"{video_id}.txt"
        )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(text)

        print(f"Saved {file_path}")

    except Exception as e:

        print(f"Failed : {video_id}")

        print(e)

print("Finished")