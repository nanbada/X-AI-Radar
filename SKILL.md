---
name: x-ai-radar
description: "최근 24시간 내 X(Twitter) AI/Agents 급상승 포스트(Velocity Score), GitHub Trending, Hacker News 및 초·중등 교육 블로그 아이템 3종을 17초 만에 통합 수집·분석하여 일일 리포트 및 텔레그램 알림을 발송합니다."
---

# x-ai-radar & edu-blog-radar Skills (v2.2)

Antigravity의 `Browser Subagent`와 **Gemini 3.7 Flash**를 결합하여 다중 도메인 인텔리전스를 초고속 수집하고, 텔레그램(`@Radar4All_bot`)으로 실시간 한국어 브리핑을 제공하는 통합 스킬입니다.

## 🎯 트리거 (Triggers)

### 1. AI & Tech Radar
- 슬래시 커맨드: `/x-ai-radar`
- 자연어 명령:
  - `"X AI 핫랭킹 돌려줘"`
  - `"최근 24시간 AI Agents 및 GitHub 인기 레포 분석해줘"`
  - `"오늘자 AI & Agents 종합 인텔리전스 리포트 생성해줘"`

### 2. Edu-Blog Radar
- 슬래시 커맨드: `/edu-blog-radar`
- 자연어 명령:
  - `"초등 중등 블로그 아이템 추천해줘"`
  - `"오늘자 교육 및 학부모 블로그 아이템 3가지 뽑아줘"`
  - `"시즌별 공부법 및 학부모 꿀팁 기획서 생성해줘"`

---

## 🛠️ v2.2 듀얼 엔진 아키텍처

1. **X-AI-Radar Engine (`scripts/collector.py`)**:
   - CDP 미디어 리소스 블로킹(`*.mp4`, `*.jpg` 차단)으로 17초 내 쾌속 수집.
   - 상태 메모리(`data/history.json`) 기반의 **Velocity Score** 산출.
   - 해외 기술 트윗을 한국어로 즉시 번역하여 텔레그램 발송.
2. **Edu-Blog Radar Engine (`scripts/edu_collector.py`)**:
   - 네이버 VIEW / 학부모 검색 트렌드 분석.
   - **초등 재미있는 공부법 / 중등 내신 플래너 / 시즌별 학습 아이템 3종** 자동 기획.
   - 제목 3세트 + 3단 본문 구성 + SEO 해시태그 리포트 생성 및 텔레그램 발송.
