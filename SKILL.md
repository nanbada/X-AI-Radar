---
name: x-ai-radar
description: "최근 24시간 내 X(Twitter)의 AI 및 AI Agents 급상승 포스트(Velocity Score)와 GitHub Trending, Hacker News 핵심 이슈를 통합 수집하여 일일 리포트를 생성합니다."
---

# x-ai-radar Skill (v2.0)

Antigravity의 `Browser Subagent`와 **Gemini 3.7 Flash**를 결합하여 X(Twitter) 정밀 검색 쿼리 + 홈 타임라인 + GitHub Trending AI 레포 + Hacker News 인기 토론을 자율 수집하고, 상태 메모리(`data/history.json`) 기반의 **Velocity Score(급상승 속도)**를 산출하는 종합 인텔리전스 스킬입니다.

## 🎯 트리거 (Triggers)
- 슬래시 커맨드: `/x-ai-radar`
- 자연어 명령:
  - `"X AI 핫랭킹 돌려줘"`
  - `"최근 24시간 AI Agents 및 GitHub 인기 레포 분석해줘"`
  - `"오늘자 AI & Agents 종합 인텔리전스 리포트 생성해줘"`

---

## 🛠️ v2.0 핵심 동작 메커니즘

1. **다중 소스 순회 (Multi-Source Ingestion)**:
   - X 정밀 검색 쿼리 (`(AI OR Agents OR LLM OR MCP) min_faves:50`)
   - X 프레임워크 쿼리 (`(LangGraph OR CrewAI OR AutoGen) min_faves:30`)
   - X 홈 타임라인 피드
2. **스레드 & 링크 분석 (Thread & Link Parsing)**:
   - 트윗 본문 내 `1/n` 타래글 및 GitHub / ArXiv 링크 자동 파싱
3. **상태 메모리 & Velocity Score 산출**:
   - `data/history.json`과 대조하여 시간당 조회수/북마크 증가율($\Delta / \Delta h$) 계산
   - `[NEW]`, `[RISING]`, `[HOT]` 배지 자동 부여
4. **멀티 플랫폼 어댑터 병합**:
   - GitHub Trending AI 오픈소스 TOP 5
   - Hacker News AI 토론 TOP 5
5. **리포트 & 웹훅 배포**:
   - `/Users/nanbada/projects/X-AI-Radar/reports/x-ai-radar-YYYY-MM-DD.md` 저장
   - Slack / Discord / Telegram 웹훅 자동 푸시 (설정 시)
