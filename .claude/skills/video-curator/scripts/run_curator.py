#!/usr/bin/env python3
"""video-curator: Anthropic API로 신규 영상의 기획자 적합성을 판단합니다."""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)

NEW_VIDEOS_PATH = "output/new_videos.json"
CRITERIA_PATH = ".claude/skills/video-curator/references/curation_criteria.json"
SCORED_VIDEOS_PATH = "output/scored_videos.json"
BATCH_SIZE = 5
MODEL = "claude-opus-4-7"


def load_criteria():
    with open(CRITERIA_PATH, encoding="utf-8") as f:
        return json.load(f)


def evaluate_batch(client, videos, criteria):
    categories_str = ", ".join(criteria["categories"])
    preferred = json.dumps(criteria["inclusion_rules"]["preferred_topics"], ensure_ascii=False)
    excluded = json.dumps(criteria["inclusion_rules"]["excluded_topics"], ensure_ascii=False)
    weights = criteria["scoring_weights"]

    videos_text = "\n\n".join(
        f"[{i+1}] video_id: {v['video_id']}\n제목: {v['title']}\n채널: {v['channel']}\n설명: {v.get('description', '')[:300]}"
        for i, v in enumerate(videos)
    )

    prompt = f"""당신은 기획자(PM, 서비스 기획, 콘텐츠 기획)를 위한 AI 유튜브 영상 큐레이터입니다.

## 큐레이션 기준
- 대상 독자: {criteria['inclusion_rules']['target_audience']}
- 선호 주제: {preferred}
- 제외 주제: {excluded}
- 카테고리: {categories_str}
- 합격 기준: {criteria['threshold']}점 이상

## 점수 계산 (가중 평균)
- planner_relevance(기획자 관련성) × {weights['planner_relevance']}
- practicality(실무 활용도) × {weights['practicality']}
- recency(최신성) × {weights['recency']}

## 평가할 영상
{videos_text}

각 영상을 평가하여 아래 JSON 배열만 반환하세요. 다른 텍스트 없이 JSON만 출력하세요.

```json
[
  {{
    "video_id": "원본 video_id 그대로",
    "title": "원본 제목",
    "channel": "원본 채널명",
    "published_at": "원본 published_at",
    "url": "원본 url",
    "thumbnail": "원본 thumbnail",
    "category": "카테고리 하나 (위 목록에서)",
    "score": 0~100 정수,
    "summary": "기획자 관점 한줄 요약 50자 이내",
    "verdict": "include 또는 borderline 또는 exclude",
    "exclude_reason": "제외/경계 사유 또는 null"
  }}
]
```

판정 기준: score≥70=include, 40≤score<70=borderline, score<40=exclude"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.content[0].text.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    result = json.loads(content)

    # 원본 데이터로 누락 필드 보완
    video_map = {v["video_id"]: v for v in videos}
    for item in result:
        orig = video_map.get(item["video_id"], {})
        for field in ("published_at", "url", "thumbnail", "channel"):
            if not item.get(field):
                item[field] = orig.get(field, "")
        if not item.get("url"):
            item["url"] = f"https://youtube.com/watch?v={item['video_id']}"
        if not item.get("thumbnail"):
            item["thumbnail"] = f"https://img.youtube.com/vi/{item['video_id']}/mqdefault.jpg"

    return result


def main():
    if not os.path.exists(NEW_VIDEOS_PATH):
        print("new_videos.json not found, 스킵")
        with open(SCORED_VIDEOS_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
        return

    with open(NEW_VIDEOS_PATH, encoding="utf-8") as f:
        new_videos = json.load(f)

    if not new_videos:
        print("신규 영상 없음, video-curator 스킵")
        with open(SCORED_VIDEOS_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
        return

    criteria = load_criteria()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    all_scored = []

    for i in range(0, len(new_videos), BATCH_SIZE):
        batch = new_videos[i:i + BATCH_SIZE]
        print(f"  배치 {i // BATCH_SIZE + 1}/{(len(new_videos) - 1) // BATCH_SIZE + 1}: {len(batch)}개 평가 중...")

        for attempt in range(3):
            try:
                scored = evaluate_batch(client, batch, criteria)
                all_scored.extend(scored)
                print(f"    → {sum(1 for v in scored if v.get('verdict') == 'include')}개 include")
                break
            except Exception as e:
                if attempt == 2:
                    print(f"  ERROR: 배치 평가 실패 (3회 시도) - {e}", file=sys.stderr)
                else:
                    print(f"  WARN: 재시도 {attempt + 1}/3... ({e})", file=sys.stderr)

    with open(SCORED_VIDEOS_PATH, "w", encoding="utf-8") as f:
        json.dump(all_scored, f, ensure_ascii=False, indent=2)

    included = sum(1 for v in all_scored if v.get("verdict") == "include")
    excluded = sum(1 for v in all_scored if v.get("verdict") == "exclude")
    borderline = sum(1 for v in all_scored if v.get("verdict") == "borderline")
    print(f"\n평가 완료: include={included}, borderline={borderline}, exclude={excluded}")

    # curated_videos.json 병합
    subprocess.run(
        [sys.executable, ".claude/skills/video-curator/scripts/save_scored_videos.py"],
        check=False,
    )


if __name__ == "__main__":
    main()
