#!/usr/bin/env python3
"""YouTube 구독 채널에서 최신 영상을 수집합니다."""
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

CHANNEL_LIST_PATH = "docs/channel_list.md"
OUTPUT_PATH = "output/raw_videos.json"
MAX_RESULTS_PER_CHANNEL = 10
LOOKBACK_HOURS = 26 * 7  # 7일 (초기 데이터 수집용, 안정화 후 26으로 변경)


def load_channels():
    """channel_list.md에서 채널 목록을 파싱합니다.
    UC... 형식과 @handle 형식 모두 지원합니다.
    """
    channels = []
    try:
        with open(CHANNEL_LIST_PATH, encoding="utf-8") as f:
            for line in f:
                # UC... 형식: | 채널명 | UCxxxxxxxxxxxxxxxxxxxxxxxx |
                m = re.search(r'\|\s*([^|]+)\s*\|\s*(UC[A-Za-z0-9_-]{22})\s*\|', line)
                if m:
                    channels.append({"name": m.group(1).strip(), "id": m.group(2).strip(), "type": "id"})
                    continue
                # @handle 형식: | 채널명 | @handle |
                m = re.search(r'\|\s*([^|]+)\s*\|\s*(@[A-Za-z0-9_-]+)\s*\|', line)
                if m:
                    channels.append({"name": m.group(1).strip(), "handle": m.group(2).strip(), "type": "handle"})
    except FileNotFoundError:
        print(f"WARN: {CHANNEL_LIST_PATH} not found", file=sys.stderr)
    return channels


def resolve_handle(youtube, handle):
    """@handle을 채널 ID(UC...)로 변환합니다."""
    handle_clean = handle.lstrip("@")
    response = youtube.channels().list(part="id", forHandle=handle_clean).execute()
    items = response.get("items", [])
    if items:
        return items[0]["id"]
    return None


def fetch_channel_videos(youtube, channel_id, published_after):
    response = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        type="video",
        order="date",
        publishedAfter=published_after,
        videoDuration="medium",  # 4분 이상 (숏츠 제외)
        maxResults=MAX_RESULTS_PER_CHANNEL,
    ).execute()

    videos = []
    for item in response.get("items", []):
        snippet = item["snippet"]
        title = snippet.get("title", "")
        # 제목에 숏츠 태그 있으면 추가 필터링
        if any(tag in title.lower() for tag in ["#shorts", "#쇼츠", "#short"]):
            continue
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "channel": snippet["channelTitle"],
            "channel_id": channel_id,
            "published_at": snippet["publishedAt"],
            "url": f"https://youtube.com/watch?v={item['id']['videoId']}",
            "thumbnail": snippet["thumbnails"].get("medium", {}).get("url", ""),
            "source": "channel",
        })
    return videos


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    channels = load_channels()
    if not channels:
        print("No channels configured in docs/channel_list.md")
        os.makedirs("output", exist_ok=True)
        if not os.path.exists(OUTPUT_PATH):
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump([], f)
        return

    youtube = build("youtube", "v3", developerKey=api_key)
    published_after = (datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # @handle → UC... 변환
    for ch in channels:
        if ch["type"] == "handle":
            resolved = resolve_handle(youtube, ch["handle"])
            if resolved:
                ch["id"] = resolved
                print(f"  [{ch['name']}] 핸들 {ch['handle']} → {resolved}")
            else:
                ch["id"] = None
                print(f"  WARN: [{ch['name']}] 핸들 {ch['handle']} 변환 실패", file=sys.stderr)

    all_videos = []
    for ch in channels:
        if not ch.get("id"):
            continue
        for attempt in range(3):
            try:
                videos = fetch_channel_videos(youtube, ch["id"], published_after)
                all_videos.extend(videos)
                print(f"  [{ch['name']}] {len(videos)}개 수집")
                break
            except HttpError as e:
                if attempt == 2:
                    print(f"  ERROR: [{ch['name']}] 수집 실패 (3회 시도) - {e}", file=sys.stderr)
                else:
                    print(f"  WARN: [{ch['name']}] 재시도 {attempt + 1}/3...", file=sys.stderr)

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

    print(f"\n채널 수집 완료: {len(new_unique)}개 신규 (누계: {len(merged)}개)")


if __name__ == "__main__":
    main()
