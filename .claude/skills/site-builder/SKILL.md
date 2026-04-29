# site-builder 스킬

## 역할
`output/curated_videos.json`을 읽어 정적 웹사이트(HTML + 검색 인덱스)를 생성하고 GitHub Pages에 배포한다.

## 스크립트 목록

| 스크립트 | 역할 |
|---------|------|
| build_site.py | curated_videos.json → HTML 사이트 + search_index.json 생성 |
| deploy.sh | output/site/ → GitHub Pages (gh-pages 브랜치) 배포 |

## 출력 구조
```
output/site/
  index.html              # 메인 페이지 (전체 영상 목록)
  search_index.json       # 클라이언트 사이드 검색 인덱스
  feedback.json           # 사용자 피드백 누적 (초기: [])
  categories/
    AI_툴_활용.html
    AI_트렌드.html
    업무_자동화.html
    프롬프트_엔지니어링.html
    기획_인사이트.html
```

## 환경변수 (deploy.sh)
- `GITHUB_TOKEN` — GitHub 배포 토큰
- `GITHUB_REPOSITORY` — 배포 대상 저장소 (owner/repo 형식)

## 피드백 연동
각 영상 카드에 👍/👎 버튼 → `window.FEEDBACK_ENDPOINT`로 POST
- Formspree 사용 시: `index.html`의 `FEEDBACK_ENDPOINT` 값을 Formspree URL로 교체
- 미설정 시: localStorage에 임시 저장
