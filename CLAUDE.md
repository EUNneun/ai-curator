# AI 영상 큐레이션 에이전트

## 역할
기획자를 위한 AI 관련 유튜브 영상을 매일 자동 수집·분류·추천하고 GitHub Pages 웹사이트를 업데이트하는 오케스트레이터.

## 실행 환경
- Python 3.11+
- 환경변수: `YOUTUBE_API_KEY`, `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`
- 실행 위치: 프로젝트 루트 (`ai-video-curator/`)

---

## 전체 워크플로우 (STEP 1~6 순차 실행)

### STEP 1: 영상 수집
```bash
python .claude/skills/youtube-collector/scripts/fetch_channel_videos.py
python .claude/skills/youtube-collector/scripts/search_keyword_videos.py
```
- 결과: `output/raw_videos.json` (누적)
- 오류 시: 개별 채널/키워드 실패는 스킵 후 계속, 최대 3회 재시도

### STEP 2: 중복 제거
```bash
python .claude/skills/youtube-collector/scripts/dedup_filter.py
```
- 결과: `output/new_videos.json`
- `new_videos.json`이 비어있으면 → **STEP 5로 건너뜀**

### STEP 3: 적합성 판단 (video-curator 서브에이전트)
- 조건: `new_videos.json`에 1건 이상
- **위임 대상**: `/.claude/agents/video-curator/AGENT.md`
- 자동화 모드 (GitHub Actions): `python .claude/skills/video-curator/scripts/run_curator.py`
- 결과: `output/scored_videos.json`
- 오류 시: 최대 2회 재시도 → 실패 시 스킵 + 로그

### STEP 4: 피드백 반영 (feedback-learner 서브에이전트, 조건부)
- 조건: `output/site/feedback.json`의 미처리(`processed: false`) 피드백 **10건 이상**
- **위임 대상**: `/.claude/agents/feedback-learner/AGENT.md`
- 자동화 모드: `python .claude/skills/feedback-learner/scripts/run_feedback_learner.py`
- 결과: 갱신된 `curation_criteria.json`
- 조건 불충족 시: 스킵 (기존 기준 유지)

### STEP 5: 큐레이션 결과 병합 + 사이트 생성
```bash
python .claude/skills/video-curator/scripts/save_scored_videos.py
python .claude/skills/site-builder/scripts/build_site.py
```
- 결과: `output/site/index.html`, 카테고리 페이지, `search_index.json`
- 오류 시: 1회 재시도 → 실패 시 에스컬레이션 (GitHub Issue 생성)

### STEP 6: 배포
```bash
bash .claude/skills/site-builder/scripts/deploy.sh
```
- 결과: GitHub Pages 배포
- 오류 시: 1회 재시도 → 실패 시 에스컬레이션

---

## 파일 경로 규칙

| 파일 | 경로 | 설명 |
|------|------|------|
| raw_videos.json | output/raw_videos.json | STEP 1 산출물, 매 실행 시 갱신 |
| new_videos.json | output/new_videos.json | STEP 2 산출물, 중복 제거 후 |
| scored_videos.json | output/scored_videos.json | STEP 3 산출물, LLM 판단 결과 |
| curated_videos.json | output/curated_videos.json | 누적 큐레이션 결과 (전체 이력) |
| run_log.json | output/run_log.json | 실행 로그 |
| feedback.json | output/site/feedback.json | 사용자 피드백 누적 |
| curation_criteria.json | .claude/skills/video-curator/references/curation_criteria.json | 큐레이션 기준 |

---

## 에러 처리 원칙

1. **재시도**: STEP 1, 3 → 최대 3회 / STEP 5, 6 → 최대 2회
2. **부분 실패 허용**: 개별 채널/키워드 수집 실패는 스킵하고 계속 진행
3. **에스컬레이션**: STEP 5, 6 최종 실패 시 GitHub Issue 자동 생성
4. **로그 필수**: 모든 오류는 `output/run_log.json`에 기록

## 실행 로그 형식

```json
{
  "run_date": "2025-01-01T07:00:00+09:00",
  "steps": {
    "step1": {"status": "success", "collected": 25},
    "step2": {"status": "success", "new_videos": 10},
    "step3": {"status": "success", "included": 7, "excluded": 3},
    "step4": {"status": "skipped", "reason": "피드백 부족 (3건 < 10건)"},
    "step5": {"status": "success"},
    "step6": {"status": "success"}
  }
}
```

---

## 서브에이전트 호출 조건 요약

| 에이전트 | 트리거 | 위치 |
|---------|--------|------|
| video-curator | new_videos.json ≥ 1건 | .claude/agents/video-curator/AGENT.md |
| feedback-learner | 미처리 피드백 ≥ 10건 | .claude/agents/feedback-learner/AGENT.md |

---

## 현재 운영 현황 (2026-04-30 기준)

### API 키 상태
- `YOUTUBE_API_KEY`: 등록 완료 (GitHub Secrets)
- `ANTHROPIC_API_KEY`: 미등록 → **DUMMY_MODE=true** 로 운영 중 (모든 영상 include, 요약 없음)
  - Anthropic API 키 등록 후 `daily_update.yml`의 `DUMMY_MODE: 'true'` → `'false'` 로 변경 필요

### 수집 설정
- 수집 기간: **7일** (초기 데이터 수집용, 안정화 후 26시간으로 변경 예정)
- 숏츠 제외: `videoDuration=medium` (4분 이상만 수집)
- 모니터링 채널: 일잘러 장피엠(`UCV_fT7iybE1rQeVGW-qLCiA`), Matt Wolfe(`@mreflow`)
- 검색 키워드: `docs/keyword_list.md` 참고

### YouTube API 할당량
- 하루 10,000유닛 제한, 리셋 시각: **매일 오후 4시 KST**
- 오늘(2026-04-30) 테스트 반복 실행으로 할당량 소진 → 내일 오후 4시 이후 정상화
- **다음 작업**: API 키 2개로 할당량 2배 확보 (채널 수집용 / 키워드 검색용 분리)
  1. Google Cloud에서 프로젝트 추가 생성 → API 키 발급
  2. GitHub Secrets에 `YOUTUBE_API_KEY_2` 추가
  3. `daily_update.yml` 수정: 키워드 검색 STEP에 `YOUTUBE_API_KEY_2` 사용

### 배포 주소
- https://EUNneun.github.io/ai-curator/

### 다음 구현 예정 (Phase 2)
- 카테고리 필터 + 검색 기능 UX 개선
- GOOD/BAD 피드백 버튼 Formspree 연동
