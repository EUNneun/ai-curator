# video-curator 스킬

## 역할
video-curator 에이전트의 LLM 판단 결과를 파일로 저장하고, `curated_videos.json`에 병합한다.

## 스크립트 목록

| 스크립트 | 역할 |
|---------|------|
| run_curator.py | LLM(Anthropic API)으로 new_videos 평가 → scored_videos.json 생성 |
| save_scored_videos.py | scored_videos.json 검증 + curated_videos.json 병합 |

## 실행 순서
```bash
python .claude/skills/video-curator/scripts/run_curator.py
python .claude/skills/video-curator/scripts/save_scored_videos.py
```

## 환경변수
- `ANTHROPIC_API_KEY` — Anthropic API 키 (run_curator.py 전용)

## 참조 파일
- `references/curation_criteria.json` — 현재 큐레이션 기준 (피드백으로 갱신됨)

## 점수 임계값
- ≥ 70: include (큐레이션 통과)
- 40~69: borderline (제외 + 사유 기록)
- < 40: exclude (제외 + 사유 기록)
