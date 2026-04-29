#!/usr/bin/env python3
"""curated_videos.json을 읽어 정적 웹사이트를 생성합니다."""
import html
import json
import os
import sys
from datetime import datetime, timezone

CURATED_PATH = "output/curated_videos.json"
SITE_DIR = "output/site"
TEMPLATE_DIR = ".claude/skills/site-builder/references/site_template"
CATEGORIES = ["AI 툴 활용", "AI 트렌드", "업무 자동화", "프롬프트 엔지니어링", "기획 인사이트"]


def load_curated():
    if not os.path.exists(CURATED_PATH):
        return []
    with open(CURATED_PATH, encoding="utf-8") as f:
        return json.load(f)


def search_index(videos):
    return [
        {
            "id": v["video_id"],
            "title": v.get("title", ""),
            "summary": v.get("summary", ""),
            "category": v.get("category", ""),
            "channel": v.get("channel", ""),
        }
        for v in videos
    ]


def video_card(v):
    vid = html.escape(v["video_id"])
    title = html.escape(v.get("title", ""))
    channel = html.escape(v.get("channel", ""))
    category = html.escape(v.get("category", ""))
    summary = html.escape(v.get("summary", ""))
    url = html.escape(v.get("url", f"https://youtube.com/watch?v={v['video_id']}"))
    thumb = html.escape(v.get("thumbnail") or f"https://img.youtube.com/vi/{v['video_id']}/mqdefault.jpg")
    score = v.get("score", 0)
    return f"""    <div class="video-card" data-category="{category}" data-id="{vid}">
      <a href="{url}" target="_blank" rel="noopener">
        <img class="thumbnail" src="{thumb}" alt="{title}" loading="lazy">
      </a>
      <div class="card-body">
        <span class="category-tag">{category}</span>
        <h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
        <p class="summary">{summary}</p>
        <div class="card-meta">
          <span class="channel">{channel}</span>
          <span class="score">점수 {score}</span>
        </div>
        <div class="feedback-buttons">
          <button class="btn-good" onclick="sendFeedback('{vid}','GOOD')" title="유용해요">👍</button>
          <button class="btn-bad" onclick="sendFeedback('{vid}','BAD')" title="별로예요">👎</button>
        </div>
      </div>
    </div>"""


def build_page(videos, css, js, title_suffix=""):
    tabs = "\n".join(
        f'      <button class="tab-btn" data-cat="{c}" onclick="filterByCategory(this,\'{c}\')">{c}</button>'
        for c in CATEGORIES
    )
    cards = "\n".join(video_card(v) for v in videos)
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    idx_json = json.dumps(search_index(videos), ensure_ascii=False)
    page_title = f"AI 영상 큐레이션{title_suffix}"
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title} | 기획자를 위한 AI 유튜브</title>
  <style>{css}</style>
</head>
<body>
  <header>
    <h1><a href="../index.html" style="color:inherit;text-decoration:none">AI 영상 큐레이션</a></h1>
    <p class="subtitle">기획자를 위한 AI 관련 유튜브 영상 추천</p>
    <p class="updated">마지막 업데이트: {updated} | {len(videos)}개</p>
  </header>
  <nav class="filter-nav">
    <div class="search-box">
      <input type="text" id="search-input" placeholder="영상 검색..." oninput="handleSearch(this.value)">
    </div>
    <div class="tab-buttons">
      <button class="tab-btn active" data-cat="all" onclick="filterByCategory(this,'all')">전체</button>
{tabs}
    </div>
  </nav>
  <main>
    <div class="video-grid" id="video-grid">
{cards}
    </div>
    <div id="no-results" class="hidden">검색 결과가 없습니다.</div>
  </main>
  <script>
    const SEARCH_INDEX = {idx_json};
    const FEEDBACK_ENDPOINT = '';
  </script>
  <script>{js}</script>
</body>
</html>"""


def main():
    videos = load_curated()
    os.makedirs(SITE_DIR, exist_ok=True)
    os.makedirs(os.path.join(SITE_DIR, "categories"), exist_ok=True)

    css_path = os.path.join(TEMPLATE_DIR, "style.css")
    js_path = os.path.join(TEMPLATE_DIR, "app.js")
    css = open(css_path, encoding="utf-8").read() if os.path.exists(css_path) else ""
    js = open(js_path, encoding="utf-8").read() if os.path.exists(js_path) else ""

    if not css:
        print("WARN: style.css not found", file=sys.stderr)
    if not js:
        print("WARN: app.js not found", file=sys.stderr)

    # index.html
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_page(videos, css, js))
    print(f"index.html 생성: {len(videos)}개 영상")

    # 카테고리 페이지
    for cat in CATEGORIES:
        cat_videos = [v for v in videos if v.get("category") == cat]
        safe = cat.replace(" ", "_").replace("/", "_")
        cat_path = os.path.join(SITE_DIR, "categories", f"{safe}.html")
        with open(cat_path, "w", encoding="utf-8") as f:
            f.write(build_page(cat_videos, css, js, f" — {cat}"))
        print(f"  {cat}: {len(cat_videos)}개")

    # search_index.json
    with open(os.path.join(SITE_DIR, "search_index.json"), "w", encoding="utf-8") as f:
        json.dump(search_index(videos), f, ensure_ascii=False, indent=2)
    print("search_index.json 생성 완료")

    # feedback.json 초기화
    feedback_path = os.path.join(SITE_DIR, "feedback.json")
    if not os.path.exists(feedback_path):
        with open(feedback_path, "w", encoding="utf-8") as f:
            json.dump([], f)

    print("사이트 생성 완료")


if __name__ == "__main__":
    main()
