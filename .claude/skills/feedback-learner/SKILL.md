# feedback-learner 스킬

## 역할
사용자 피드백 파일을 로드하고, feedback-learner 에이전트의 분석 결과(갱신된 기준)를 저장한다.

## 스크립트 목록

| 스크립트 | 역할 |
|---------|------|
| run_feedback_learner.py | 피드백 수 확인 → 10건 이상이면 LLM 분석 실행 |
| load_feedback.py | feedback.json에서 미처리 피드백 추출 |
| save_updated_criteria.py | 갱신된 curation_criteria.json 저장 |

## 트리거 조건
미처리 피드백 10건 이상 (아니면 스킵)

## Phase 1 구현 상태
- 피드백 통계 집계 및 processed 마킹: 완료
- LLM 기반 기준 자동 조정: Phase 3에서 구현 예정
