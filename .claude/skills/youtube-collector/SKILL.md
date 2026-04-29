# youtube-collector 스킬

## 역할
YouTube Data API v3를 사용하여 지정된 채널과 키워드에서 신규 영상을 수집하고 중복을 제거한다.

## 스크립트 목록

| 스크립트 | 역할 | 입력 | 출력 |
|---------|------|------|------|
| fetch_channel_videos.py | 구독 채널 신규 영상 수집 | docs/channel_list.md | output/raw_videos.json |
| search_keyword_videos.py | 키워드 검색 수집 | docs/keyword_list.md | output/raw_videos.json (append) |
| dedup_filter.py | 중복 및 기수집 영상 제거 | output/raw_videos.json | output/new_videos.json |

## 실행 순서
```bash
python .claude/skills/youtube-collector/scripts/fetch_channel_videos.py
python .claude/skills/youtube-collector/scripts/search_keyword_videos.py
python .claude/skills/youtube-collector/scripts/dedup_filter.py
```

## 환경변수
- `YOUTUBE_API_KEY` — YouTube Data API v3 키 (필수)

## API 할당량 사용량 추정

| 작업 | 유닛/호출 | 채널 10개 | 키워드 5개 |
|------|---------|---------|---------|
| search.list | 100 | 1,000 | 500 |
| 합계 | — | — | ~1,500 유닛/일 |

일 한도 10,000 유닛 대비 여유 있음.

## 수집 범위
- 채널 영상: 최근 26시간 이내 (`publishedAfter`)
- 키워드 검색: 최근 26시간 이내, 영어 (`relevanceLanguage: en`)
- 채널당 최대 10개, 키워드당 최대 5개
