# Install the following requirements.
# pip install youtube_dl youtube-transcript-api
import json

import youtube_dl
from youtube_transcript_api import YouTubeTranscriptApi


def get_all_video_links(channel_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "force_generic_extractor": True,
        "extractor_args": {"youtube:tab": "videos"},
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)
        if "entries" in result:
            return [entry["url"] for entry in result["entries"]]
        else:
            return []


def process_video(link, languages=["en"]):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(link, languages=languages)
        combined_text = " ".join(item["text"] for item in transcript)
        return {"video_url": link, "text": combined_text}
    except Exception as e:
        print(f"Error processing {link}: {e}")
        return None


def main():
    video_data = []
    failed_list = []

    # channel_url = input("https://www.youtube.com/@dzylo2861/videos")
    channel_url = "https://www.youtube.com/@dzylo2861/videos"

    video_links = get_all_video_links(channel_url)
    print(video_links)
    for link in video_links:
        result = process_video(link)
        if result:
            video_data.append(result)
        else:
            failed_list.append(link)

    with open("output.json", "w", encoding="utf-8") as json_file:
        json.dump(video_data, json_file, ensure_ascii=False, indent=2)

    print("Completed.")


if __name__ == "__main__":
    main()



# import json
# import youtube_dl
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


# def get_all_video_links(channel_url):
#     ydl_opts = {
#         "quiet": True,
#         "extract_flat": True,
#         "force_generic_extractor": True,
#         "extractor_args": {"youtube:tab": "videos"},
#     }

#     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#         result = ydl.extract_info(channel_url, download=False)
#         if "entries" in result:
#             return [entry["url"] for entry in result["entries"]]
#         return []


# def process_video(link, languages=["en"]):
#     try:
#         transcript = YouTubeTranscriptApi.get_transcript(link.split("v=")[-1], languages=languages)
#         combined_text = " ".join(item["text"] for item in transcript)
#         return {"video_url": link, "text": combined_text}

#     except NoTranscriptFound:
#         print(f"Skipping {link}: No English transcript found. Trying auto-generated...")
#         try:
#             transcript = YouTubeTranscriptApi.get_transcript(link.split("v=")[-1], languages=['hi'])  # Example fallback
#             combined_text = " ".join(item["text"] for item in transcript)
#             return {"video_url": link, "text": combined_text}
#         except NoTranscriptFound:
#             print(f"Skipping {link}: No auto-generated transcript available.")
#             return None

#     except TranscriptsDisabled:
#         print(f"Skipping {link}: Subtitles are disabled.")
#         return None

#     except Exception as e:
#         print(f"Error processing {link}: {e}")
#         return None


# def main():
#     video_data = []
#     failed_list = []

#     channel_url = "https://www.youtube.com/@dzylo2861/videos"  # Fixed URL assignment
#     video_links = get_all_video_links(channel_url)

#     for link in video_links:
#         result = process_video(link)
#         if result:
#             video_data.append(result)
#         else:
#             failed_list.append(link)

#     with open("output.json", "w", encoding="utf-8") as json_file:
#         json.dump(video_data, json_file, ensure_ascii=False, indent=2)

#     print(f"Completed. {len(video_data)} videos processed successfully, {len(failed_list)} failed.")


# if __name__ == "__main__":
#     main()
