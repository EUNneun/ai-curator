#!/usr/bin/env python3
"""키워드로 YouTube 영상을 검색하여 수집합니다."""
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("ERROR: google-api-python-client not installed. Run: pip install google-api-python-client", file=sys.stderr)
    sys.exit(1)

KEYWORD_LIST_PATH = "docs/keyword_list.md"
OUTPUT_PATH = "output/raw_videos.json"
MAX_RESULTS_PER_KEYWORD = 5
LOOKBACK_HOURS = 26


def load_keywords():
    keywords = []
    try:
        with open(KEYWORD_LIST_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                m = re.match(r'^-\s+(.+)$', line)
                if m:
                    kw = m.group(1).strip()
                    if kw and not kw.startswith('#'):
                        keywords.append(kw)
    except FileNotFoundError:
        print(f"WARN: {KEYWORD_LIST_PATH} not found", file=sys.stderr)
    return keywords


def search_videos(youtube, keyword, published_after):
    response = youtube.search().list(
        part="snippet",
        q=keyword,
        type="video",
        order="relevance",
        publishedAfter=published_after,
        relevanceLanguage="en",
        maxResults=MAX_RESULTS_PER_KEYWORD,
    ).execute()

    videos = []
    for item in response.get("items", []):
        snippet = item["snippet"]
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "channel": snippet["channelTitle"],
            "channel_id": snippet.get("channelId", ""),
            "published_at": snippet["publishedAt"],
            "url": f"https://youtube.com/watch?v={item['id']['videoId']}",
            "thumbnail": snippet["thumbnails"].get("medium", {}).get("url", ""),
            "source": "keyword",
            "keyword": keyword,
        })
    return videos


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    keywords = load_keywords()
    if not keywords:
        print("No keywords configured in docs/keyword_list.md")
        return

    youtube = build("youtube", "v3", developerKey=api_key)
    published_after = (datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_videos = []
    for kw in keywords:
        for attempt in range(3):
            try:
                videos = search_videos(youtube, kw, published_after)
                all_videos.extend(videos)
                print(f"  [{kw}] {len(videos)}개 검색")
                break
            except HttpError as e:
                if attempt == 2:
                    print(f"  ERROR: [{kw}] 검색 실패 (3회 시도) - {e}", file=sys.stderr)
                else:
                    print(f"  WARN: [{kw}] 재시도 {attempt + 1}/3...", file=sys.stderr)

    os.makedirs("output", exist_ok=True)
    existing = []
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            existing = json.load(f)

    existing_ids = {v["video_id"] for v in existing}
    new_unique = [v for v in all_videos if v["video_id"] not in existing_ids]
    merged = existing + new_unique

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"\n키워드 검색 완료: {len(new_unique)}개 신규 (누계: {len(merged)}개)")


if __name__ == "__main__":
    main()
