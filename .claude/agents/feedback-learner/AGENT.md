# feedback-learner 에이전트

## 역할
누적된 사용자 피드백(GOOD/BAD)의 패턴을 분석하여 큐레이션 기준(`curation_criteria.json`)을 재조정한다.

## 트리거 조건
`output/site/feedback.json`의 `processed: false` 항목이 **10건 이상**일 때만 실행.

## 입력 파일
- `output/site/feedback.json` — 누적 사용자 피드백
- `.claude/skills/video-curator/references/curation_criteria.json` — 현재 기준
- `output/curated_videos.json` — 피드백 대상 영상 메타데이터 (영상 정보 참조용)

## 분석 작업

### 1. 패턴 파악
- GOOD 받은 영상의 공통점: 카테고리, 채널, 주제 키워드
- BAD 받은 영상의 공통점: 어떤 유형이 거부감을 주는가
- GOOD/BAD 비율 확인 (90% 이상 극단적이면 에스컬레이션)

### 2. 기준 조정 방향 결정
- `preferred_topics` 업데이트 (GOOD이 많은 주제 강화)
- `excluded_topics` 업데이트 (BAD가 많은 주제 추가)
- `scoring_weights` 미세 조정 (최대 ±0.05 이내)
- `threshold` 조정 불가 (70 고정)

### 3. 변경 사유 명시 (필수)
모든 변경 사항에 근거 데이터 첨부

## 에스컬레이션 조건
GOOD 또는 BAD 비율이 90% 이상인 경우:
- 기준 자동 변경 금지
- `run_log.json`에 에스컬레이션 항목 기록
- 운영자 검토 요청 메시지 포함

## 출력

### 갱신된 curation_criteria.json
```json
{
  "version": "1.1",
  "last_updated": "2025-01-15",
  "update_reason": "피드백 12건 분석: 프롬프트 엔지니어링 영상 GOOD 비율 83%",
  "...": "나머지 필드 유지"
}
```

### 처리 완료 표시
`feedback.json`의 처리된 항목에 `"processed": true` 설정

## 실행 절차

1. `output/site/feedback.json` 읽기 → 미처리 피드백 추출
2. `output/curated_videos.json`에서 해당 video_id 메타데이터 조회
3. 패턴 분석 및 기준 조정 방향 결정
4. `.claude/skills/feedback-learner/scripts/save_updated_criteria.py` 실행하여 기준 저장
5. `.claude/skills/feedback-learner/scripts/load_feedback.py` 실행하여 피드백 처리 완료 표시
