#!/usr/bin/env python3
"""scored_videos.json을 검증하고 curated_videos.json에 병합합니다."""
import json
import os
import sys
from datetime import datetime, timezone

SCORED_VIDEOS_PATH = "output/scored_videos.json"
CURATED_VIDEOS_PATH = "output/curated_videos.json"


def validate(v):
    required = ["video_id", "title", "channel", "published_at", "url", "category", "score", "summary", "verdict"]
    for field in required:
        if field not in v:
            return False, f"필드 누락: {field}"
    if not isinstance(v["score"], (int, float)) or not (0 <= v["score"] <= 100):
        return False, f"score 범위 오류: {v['score']}"
    if v["verdict"] in ("exclude", "borderline") and not v.get("exclude_reason"):
        return False, "exclude/borderline에 exclude_reason 누락"
    return True, None


def main():
    if not os.path.exists(SCORED_VIDEOS_PATH):
        print("scored_videos.json not found", file=sys.stderr)
        sys.exit(1)

    with open(SCORED_VIDEOS_PATH, encoding="utf-8") as f:
        scored = json.load(f)

    valid_videos = []
    for v in scored:
        ok, err = validate(v)
        if ok:
            valid_videos.append(v)
        else:
            print(f"WARN: [{v.get('video_id', '?')}] 검증 실패 - {err}", file=sys.stderr)

    existing = []
    if os.path.exists(CURATED_VIDEOS_PATH):
        with open(CURATED_VIDEOS_PATH, encoding="utf-8") as f:
            existing = json.load(f)

    existing_ids = {v["video_id"] for v in existing}
    now = datetime.now(timezone.utc).isoformat()
    to_add = []
    for v in valid_videos:
        if v["verdict"] == "include" and v["video_id"] not in existing_ids:
            v["scored_at"] = now
            to_add.append(v)

    merged = to_add + existing  # 최신 영상이 앞에 오도록
    with open(CURATED_VIDEOS_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"curated_videos.json 업데이트: +{len(to_add)}개 (누계 {len(merged)}개)")


if __name__ == "__main__":
    main()
