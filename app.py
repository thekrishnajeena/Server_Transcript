import logging
import requests

# Save the original requests.get
old_get = requests.get

def new_get(*args, **kwargs):
    headers = kwargs.get("headers", {})
    if "User-Agent" not in headers:
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.93 Safari/537.36"
        )
    kwargs["headers"] = headers
    return old_get(*args, **kwargs)

# Monkey-patch requests.get
requests.get = new_get

from flask import Flask, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

@app.route('/transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        transcript_text = "\n".join(entry["text"] for entry in transcript_data)
        return jsonify({"transcript": transcript_text})
    except TranscriptsDisabled as e:
        logging.error(f"Transcript disabled for video {video_id}: {e}")
        return jsonify({"error": "Subtitles are disabled for this video"}), 404
    except Exception as e:
        logging.exception(f"Error fetching transcript for video {video_id}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
