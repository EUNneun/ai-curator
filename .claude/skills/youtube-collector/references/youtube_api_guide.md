# YouTube Data API v3 가이드

## API 키 발급
1. Google Cloud Console → 프로젝트 생성
2. YouTube Data API v3 활성화
3. 사용자 인증 정보 → API 키 생성
4. GitHub Secrets에 `YOUTUBE_API_KEY`로 저장

## 할당량 (하루 10,000 유닛)

| 메서드 | 유닛 |
|-------|------|
| search.list | 100 |
| videos.list | 1 |
| channels.list | 1 |

### 현재 사용량 추정
- 채널 10개 × search.list = 1,000 유닛
- 키워드 10개 × search.list = 1,000 유닛
- **합계: ~2,000 유닛/일** (여유 8,000 유닛)

## 채널 ID 찾는 방법
1. 채널 페이지 → 우클릭 → 페이지 소스 보기
2. `"channelId"` 검색
3. 또는 URL: `youtube.com/@channelname` → 브라우저 콘솔에서 `ytInitialData` 검색

## publishedAfter 포맷
```
YYYY-MM-DDTHH:MM:SSZ  (RFC 3339, UTC)
예: 2025-01-01T00:00:00Z
```

## 공통 오류

| 코드 | 의미 | 대응 |
|------|------|------|
| 403 quotaExceeded | 할당량 초과 | 내일 재시도 |
| 404 channelNotFound | 채널 ID 오류 | channel_list.md 확인 |
| 400 invalidChannelId | 채널 ID 형식 오류 | UC로 시작하는 24자리 확인 |
