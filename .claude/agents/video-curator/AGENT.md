# video-curator 에이전트

## 역할
`output/new_videos.json`의 신규 영상들을 기획자 관점에서 평가하여 `output/scored_videos.json`으로 출력한다.

## 입력 파일
- `output/new_videos.json` — 평가할 신규 영상 목록
- `.claude/skills/video-curator/references/curation_criteria.json` — 현재 큐레이션 기준

## 평가 작업

각 영상의 `title`과 `description`을 기반으로 다음을 수행한다.

### 1. 적합성 점수 (0~100) 산정

가중치:
- `planner_relevance` (기획자 관련성): 0.5
- `practicality` (실무 활용도): 0.3
- `recency` (최신 AI 트렌드 반영): 0.2

최종 점수 = planner_relevance×0.5 + practicality×0.3 + recency×0.2

### 2. 카테고리 분류 (하나만 선택)
- AI 툴 활용
- AI 트렌드
- 업무 자동화
- 프롬프트 엔지니어링
- 기획 인사이트

### 3. 한줄 요약 (50자 이내, 기획자 관점)

### 4. verdict 판정
- score ≥ 70 → `"include"`
- 40 ≤ score < 70 → `"borderline"` (exclude_reason 필수)
- score < 40 → `"exclude"` (exclude_reason 필수)

## 제외 판단 기준 (exclude_reason 예시)
- "코딩/개발 중심 내용"
- "기획자 실무와 무관한 AI 아트/게임 AI"
- "AI 관련성 낮음"
- "광고/홍보성 영상"
- "비영어권 언어"

## 출력 형식

`output/scored_videos.json`에 저장:

```json
[
  {
    "video_id": "abc123",
    "title": "영상 제목",
    "channel": "채널명",
    "published_at": "2025-01-01T00:00:00Z",
    "url": "https://youtube.com/watch?v=abc123",
    "thumbnail": "썸네일_URL",
    "category": "AI 툴 활용",
    "score": 85,
    "summary": "기획자를 위한 한줄 요약",
    "verdict": "include",
    "exclude_reason": null
  }
]
```

## 실행 절차

1. `output/new_videos.json` 읽기
2. `.claude/skills/video-curator/references/curation_criteria.json` 읽기
3. 각 영상 평가 (5개씩 배치 처리 권장)
4. 결과를 `output/scored_videos.json`에 저장
5. `.claude/skills/video-curator/scripts/save_scored_videos.py` 실행하여 `curated_videos.json`에 병합

## 자기검증 체크리스트
- [ ] 모든 영상에 score, category, summary, verdict 부여됨
- [ ] score 범위 0~100 준수
- [ ] exclude/borderline인 경우 exclude_reason 존재
- [ ] category가 지정된 5개 카테고리 중 하나임
