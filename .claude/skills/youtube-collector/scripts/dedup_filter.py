#!/usr/bin/env python3
"""중복 제거 및 기수집 영상 필터링."""
import json
import os
import sys

RAW_VIDEOS_PATH = "output/raw_videos.json"
CURATED_VIDEOS_PATH = "output/curated_videos.json"
SCORED_VIDEOS_PATH = "output/scored_videos.json"
NEW_VIDEOS_PATH = "output/new_videos.json"


def main():
    if not os.path.exists(RAW_VIDEOS_PATH):
        print("raw_videos.json not found, 신규 영상 없음")
        os.makedirs("output", exist_ok=True)
        with open(NEW_VIDEOS_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
        return

    with open(RAW_VIDEOS_PATH, encoding="utf-8") as f:
        raw_videos = json.load(f)

    # 이미 처리된 video_id 수집
    already_seen = set()
    if os.path.exists(CURATED_VIDEOS_PATH):
        with open(CURATED_VIDEOS_PATH, encoding="utf-8") as f:
            curated = json.load(f)
            already_seen |= {v["video_id"] for v in curated}

    if os.path.exists(SCORED_VIDEOS_PATH):
        with open(SCORED_VIDEOS_PATH, encoding="utf-8") as f:
            scored = json.load(f)
            already_seen |= {v["video_id"] for v in scored}

    # raw_videos 내부 중복 제거 + 기수집 제외
    seen_today = set()
    new_videos = []
    for v in raw_videos:
        vid = v["video_id"]
        if vid not in seen_today and vid not in already_seen:
            seen_today.add(vid)
            new_videos.append(v)

    with open(NEW_VIDEOS_PATH, "w", encoding="utf-8") as f:
        json.dump(new_videos, f, ensure_ascii=False, indent=2)

    print(f"중복 제거: {len(raw_videos)}개 → {len(new_videos)}개 신규")
    if not new_videos:
        print("신규 영상 없음 → STEP 3~4 스킵")
    sys.exit(0)


if __name__ == "__main__":
    main()
