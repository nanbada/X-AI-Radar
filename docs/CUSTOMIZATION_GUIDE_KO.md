# ⚙️ X-AI-Radar & Edu-Blog Radar: 상세 커스터마이징 & 알림 채널 관리 가이드

본 문서는 검색 소스, 주제(Topic), 검색 쿼리, 노이즈 필터링, 그리고 알림 채널(텔레그램 봇, 슬랙, 디스코드)을 손쉽게 변경하는 방법을 안내합니다.

---

## 🚀 1. 인터랙티브 대화형 설정 마법사 (추천)

설정 파일을 직접 열지 않고도, 대화형 CLI 마법사를 통해 검색 쿼리, 키워드, 텔레그램 봇 토큰을 손쉽게 확인하고 변경할 수 있습니다:

```bash
python radar.py --config
```

```text
========================================================
⚙️ X-AI-Radar & Edu-Blog Radar Configuration Wizard
========================================================
  [1] 📋 현재 활성화된 설정 및 채널 조회
  [2] 📡 X.com 검색 쿼리 및 소스 관리 (추가/삭제)
  [3] 🏷️ 가산점(+150점) 및 제외 키워드 관리
  [4] 🔔 텔레그램 / 슬랙 / 디스코드 채널 등록 및 변경
  [5] 🧪 등록된 모든 알림 채널 테스트 발송
  [Q] 마법사 종료
========================================================
```

---

## 📡 2. 검색 소스 및 주제(Topic) 변경 방법

### A. X(Twitter) 검색 쿼리 수정 (`config.yaml`)
`config.yaml`의 `browser.search_queries` 항목에 X 공식 검색 연산자를 조합한 URL을 등록합니다:

```yaml
browser:
  search_queries:
    # 쿼리 1: AI Agents 및 추론 모델 (좋아요 50개 이상만 수집)
    - "https://x.com/search?q=(AI%20OR%20Agents%20OR%20Reasoning%20OR%20MCP)%20min_faves%3A50&f=live"
    
    # 쿼리 2: 멀티 에이전트 프레임워크 (LangGraph, CrewAI, AutoGen)
    - "https://x.com/search?q=(LangGraph%20OR%20CrewAI%20OR%20AutoGen)%20min_faves%3A30&f=live"
```

#### 💡 유용한 X 검색 연산자 모음:
* `min_faves:50`: 좋아요 50개 이상의 검증된 포스트만 필터링
* `lang:ko` 또는 `lang:en`: 특정 언어로 작성된 트윗만 필터링
* `-filter:replies`: 단순 댓글 타래를 제외하고 원문 포스트만 수집
* `(키워드A OR 키워드B)`: 여러 키워드 중 하나라도 포함된 포스트 탐색

---

### B. 가산점 및 제외 키워드 관리 (`config.yaml`)
본문에 해당 키워드가 포함되면 자동으로 **+150점의 Heat Score 보너스**가 주어집니다:

```yaml
topics:
  # 가산점(+150점) 부여 키워드
  boost_keywords:
    - "Agent"
    - "LangGraph"
    - "CrewAI"
    - "MCP"
    - "Claude"
    - "DeepSeek"

  # 리포트에서 원천 배제할 제외 키워드
  exclude_keywords:
    - "airdrop"
    - "giveaway"
    - "memecoin"
    - "football"
    - "transfer"
```

---

### C. 초·중등 교육 블로그 기획 쿼리 변경 (`scripts/adapters/naver_edu.py`)
Edu-Blog Radar가 탐색하는 네이버/웹 검색 주제를 변경하고 싶을 때:

```python
SEARCH_QUERIES = [
    "초등 재미있는 공부법",
    "초등 자기주도학습 습관",
    "중등 내신 공부법",
    "중학교 시험 플래너",
    "시즌별 초중등 학습 아이템",
    "학부모 교육 고민 꿀팁"
]
```

---

## 🔔 3. 알림 채널 변경 방법 (텔레그램, 슬랙, 디스코드)

모든 민감한 토큰과 웹훅 URL은 Git에 노출되지 않도록 **[`.env`](file:///Users/nanbada/projects/X-AI-Radar/.env)** 파일에 안전하게 보관됩니다:

```env
# 1. AI 테크 레이더 텔레그램 봇 (@Radar4All_bot)
TELEGRAM_BOT_TOKEN="8969095857:AAFK1_v2QpLFKy4yx32g6ktocd4ZQSnyszY"
TELEGRAM_CHAT_ID="6350373048"

# 2. 교육 블로그 레이더 텔레그램 봇 (@edunewsradar_bot / 학습블로그 아이템)
EDU_TELEGRAM_BOT_TOKEN="8376644109:AAFRgtiM5kJ7h4Qu5Gl2B602wYIj3GhXms4"
EDU_TELEGRAM_CHAT_ID="6350373048"

# 3. 선택 사항 (슬랙 & 디스코드 웹훅)
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

---

## 📋 4. 복사해서 바로 쓰는 도메인 프리셋

### 프리셋 1: 🤖 로보틱스 & 피지컬 AI
```yaml
browser:
  search_queries:
    - "https://x.com/search?q=(Robotics%20OR%20Humanoid%20OR%20PhysicalAI)%20min_faves%3A30&f=live"
    - "https://x.com/search?q=(FigureAI%20OR%20Optimus%20OR%20Unitree)%20min_faves%3A20&f=live"
topics:
  boost_keywords: ["Humanoid", "ROS2", "Actuator", "Physical AI", "Dexterity"]
```

### 프리셋 2: 📈 퀀트 금융 & 트레이딩 AI
```yaml
browser:
  search_queries:
    - "https://x.com/search?q=(Quant%20OR%20AlgorithmicTrading%20OR%20FinLLM)%20min_faves%3A30&f=live"
topics:
  boost_keywords: ["Backtest", "OrderBook", "Alpha", "Pairs Trading", "HFT"]
```

### 프리셋 3: 🇰🇷 한국어 테크 & 스타트업 트렌드
```yaml
browser:
  search_queries:
    - "https://x.com/search?q=(인공지능%20OR%20생성형AI%20OR%20스타트업)%20min_faves%3A10&f=live"
topics:
  boost_keywords: ["거대언어모델", "에이전트", "LLM", "오픈소스", "파인튜닝"]
```
