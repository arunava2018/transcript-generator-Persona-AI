import os
from youtube_transcript_api import YouTubeTranscriptApi
from video_ids import PIYUSH_VIDEO_IDS, HITESH_VIDEO_IDS

# ---------------------------------------
# CONFIG
# ---------------------------------------

PERSONA = "piyush"  # Change this to "PIYUSH" to download PiYush's transcripts

LANGUAGES = ["hi", "en"]

OUTPUT_DIR = f"transcripts/{PERSONA}"
    
os.makedirs(OUTPUT_DIR, exist_ok=True)

ytt = YouTubeTranscriptApi()

# ---------------------------------------
# Download
# ---------------------------------------

for video_id in HITESH_VIDEO_IDS if PERSONA == "hitesh" else PIYUSH_VIDEO_IDS:

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