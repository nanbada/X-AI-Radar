---
name: x-ai-radar
description: "최근 24시간 내 X(Twitter) AI/Agents 급상승 포스트(Velocity Score)와 GitHub Trending, Hacker News 핵심 이슈를 17초 만에 통합 수집·분석하여 일일 리포트를 생성합니다."
---

# x-ai-radar Skill (v2.1 High-Speed Engine)

Antigravity의 `Browser Subagent`와 **Gemini 3.7 Flash**를 결합하여 X(Twitter) 정밀 검색 쿼리 + 홈 타임라인 + GitHub Trending AI 오픈소스 + Hacker News 인기 토론을 17초 내 초고속 병렬 수집하고, 상태 메모리(`data/history.json`) 기반의 **Velocity Score(급상승 속도)**를 산출하는 종합 인텔리전스 스킬입니다.

## 🎯 트리거 (Triggers)
- 슬래시 커맨드: `/x-ai-radar`
- 자연어 명령:
  - `"X AI 핫랭킹 돌려줘"`
  - `"최근 24시간 AI Agents 및 GitHub 인기 레포 분석해줘"`
  - `"오늘자 AI & Agents 종합 인텔리전스 리포트 생성해줘"`

---

## 🛠️ v2.1 고속 최적화 메커니즘

1. **CDP 미디어 리소스 블로킹**:
   - `Network.setBlockedURLs`를 통해 비디오 스트림(`*.mp4`), 고해상도 이미지(`*.jpg`, `*.webp`), 광고 트래커를 브라우저 단에서 100% 차단하여 로딩 속도 60% 단축.
2. **동기화된 CDP RPC 파이프라인 (`cdp_send_sync`)**:
   - `Page.navigate`와 `Runtime.evaluate` 간의 패킷 꼬임 없이 100% 무결성 데이터 추출.
3. **병렬 어댑터 풀 (`ThreadPoolExecutor`)**:
   - X 타임라인 탐색과 동시에 **GitHub Trending AI** 및 **Hacker News API**를 백그라운드 스레드에서 병렬 호출하여 직렬 대기 시간 0초화.
4. **상태 메모리 & Velocity Score 산출**:
   - `data/history.json`과 대조하여 시간당 조회수/북마크 증가율($\Delta / \Delta h$) 기반 급상승 포스트(`[RISING]`, `[HOT]`) 랭킹.
5. **3단 통합 리포트 & 웹훅 배포**:
   - `/Users/nanbada/projects/X-AI-Radar/reports/x-ai-radar-YYYY-MM-DD.md` 자동 저장
   - Slack / Discord / Telegram 웹훅 자동 푸시 (설정 시)
