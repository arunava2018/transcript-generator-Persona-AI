from youtube_transcript_api import YouTubeTranscriptApi


video_id = "CvuNdXB_UQg"
ytt_api = YouTubeTranscriptApi()

fetched_transcript = ytt_api.fetch(video_id, languages=['hi'])

for snippet in fetched_transcript:
    print(snippet.text)

# indexable
last_snippet = fetched_transcript[-1]

# provides a length
snippet_count = len(fetched_transcript)
print("Done")