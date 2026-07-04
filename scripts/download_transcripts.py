import os
from youtube_transcript_api import YouTubeTranscriptApi

# ---------------------------------------
# CONFIG
# ---------------------------------------

PERSONA = "hitesh"

VIDEO_IDS = [
    "CvuNdXB_UQg",
    "02ctXgIHMb0",
    "tKOuP4nP5jE",
    "ZmjBN_SY5xo",
    "v=5n_utsAVI-g",
    "VCqiwPs8ISE",
    "1YzNl1tkAik",
    "5YqP18Gyop0",
    "B5LZnYYoLtY",
    "dZyQNy3-HjU",
    "hYIb2xs0vvk",
    "Csr2iU8O_rw",
    "g7T0TbcgDdY",
    "WepZXtywOAs",
    "FHCKOP25Z1A",
    "kYeDJhA4XIw",
    "pERZpUPHBFI",
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