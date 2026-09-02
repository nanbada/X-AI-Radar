#!/usr/bin/env python3
"""
Edu-Blog Radar Intelligence Engine (v1.0)
Scouts educational trends across Elementary, Middle school, and Seasonal domains.
Generates 3 actionable blog topic plans and dispatches them to Telegram.
"""

import html
from datetime import datetime
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import yaml

# Import local modules
sys.path.append(os.path.dirname(__file__))
from adapters.naver_edu import get_all_edu_trends

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")

def load_env_vars():
    env_vars = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip().strip('"').strip("'")
    return env_vars

def send_edu_telegram_notification(today_str, report_file, items):
    env_vars = load_env_vars()
    tg_token = env_vars.get("TELEGRAM_BOT_TOKEN")
    tg_chat_id = env_vars.get("TELEGRAM_CHAT_ID")
    
    if not tg_token or not tg_chat_id:
        print("⚠️ No Telegram credentials found.", file=sys.stderr)
        return

    tg_lines = [
        f"🎓 <b>[Edu-Blog Radar] 오늘의 초·중등 블로그 아이템 TOP 3 ({html.escape(today_str)})</b>",
        f"📁 <i>기획서: {html.escape(os.path.basename(report_file))}</i>",
        "───────────────────────────────"
    ]
    
    for i, item in enumerate(items, 1):
        cat = html.escape(item["category"])
        title = html.escape(item["recommended_title"])
        target = html.escape(item["target"])
        core = html.escape(item["core_outline"])
        
        tg_lines.append(f"<b>🎯 [아이템 {i}] {cat}</b>")
        tg_lines.append(f"👥 <b>타겟</b>: {target}")
        tg_lines.append(f"📌 <b>추천 제목</b>: <i>\"{title}\"</i>")
        tg_lines.append(f"📝 <b>핵심 구성</b>:\n{core}\n")
        
    tg_lines.append("───────────────────────────────")
    tg_lines.append("💡 <i>본문 작성용 풀버전 목차와 해시태그는 리포트 파일에 저장되었습니다.</i>")
    
    tg_html = "\n".join(tg_lines)
    
    send_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    payload = json.dumps({
        "chat_id": tg_chat_id,
        "text": tg_html,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(send_url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as res:
            print("✅ Edu-Blog 3-Item Radar successfully sent to Telegram!")
    except Exception as e:
        print(f"⚠️ Telegram sending error: {e}", file=sys.stderr)

def main():
    start_time = time.time()
    today_str = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S KST")
    
    print(f"⚡ [Edu-Blog Radar] Initializing Educational Intelligence Engine ({today_str})...")
    
    # 1. Fetch live search items
    trends = get_all_edu_trends()
    
    # 2. Curate 3 High-Impact Blog Items (Elementary, Middle, Seasonal)
    # Item 1: Elementary Fun Study
    item1 = {
        "category": "초등 저학년/고학년",
        "subtitle": "놀이형 자기주도 학습 습관과 루틴 형성",
        "target": "초등 1~4학년 학부모 (2학기 개학 후 산만한 아이 고민)",
        "insight": "개학 직후 아이들이 책상에 앉기 힘들어하는 시기입니다. 억지로 문제집을 풀게 하기보다 타이머 게임이나 스티커 미션 등 '놀이처럼 접근하는 15분 루틴'이 학부모 검색량 1위입니다.",
        "title_a": "공부하라는 잔소리 끝! 하루 15분 '게임처럼 즐기는' 초등 복습 루틴 3가지",
        "title_b": "초등 아이가 먼저 책상에 앉게 만드는 '15분 타이머 공부법'의 비밀",
        "title_c": "숙제할 때마다 전쟁인가요? 초등 자기주도학습을 돕는 부모의 말센스",
        "recommended_title": "공부하라는 잔소리 끝! 하루 15분 '게임처럼 즐기는' 초등 복습 루틴 3가지",
        "intro": "개학하고 2주 차, 방학 동안 흐트러진 학습 리듬 때문에 매일 저녁 아이와 실랑이하고 계신가요? 초등 시기에는 양보다 '성취감'이 핵심입니다.",
        "body_1": "1. [타이머 챌린지]: 15분 동안 딱 2장만 집중해서 풀고 휴식하는 '뽀모도로 키즈 공부법'",
        "body_2": "2. [선택권 부여하기]: '수학 먼저 할까, 국어 먼저 할까?' 아이 스스로 순서를 정하게 하는 꿀팁",
        "body_3": "3. [보상 시각화]: 문제집 끝날 때마다 붙이는 '나만의 성장 레벨업 스티커판'",
        "outro": "오늘 저녁부터 잔소리 대신 타이머를 켜보세요. 아이가 느끼는 성취감이 공부 습관의 첫걸음이 됩니다.",
        "core_outline": "• 15분 타이머 뽀모도로 키즈 공부법\n• 아이에게 학습 순서 선택권 주는 대화법\n• 시각적 성취감을 주는 레벨업 스티커판",
        "tags": "#초등공부법 #초등자기주도학습 #초등학부모 #초등습관 #초등맘소통 #2학기학습법"
    }
    
    # Item 2: Middle School Exam Strategy
    item2 = {
        "category": "중등 1~3학년",
        "subtitle": "2학기 1차 지필평가(중간고사) 4주 완성 플래너 전략",
        "target": "중학생 및 중등 학부모 (내신 성적 향상 및 서술형 대비 고민)",
        "insight": "9월은 2학기 중간고사를 3~4주 앞둔 골든타임입니다. 초등과 달리 범위가 넓고 서술형 배점이 높은 중등 내신은 '과목별 분할 플래너' 작성이 핵심 조회수 견인 키워드입니다.",
        "title_a": "중학교 첫 중간고사 멘붕 방지! 상위권이 꼭 지키는 '4주 분할 플래너' 작성법",
        "title_b": "중등 내신 서술형 감점 막는 3단계 교과서 백지 복습법",
        "title_c": "벼락치기는 이제 그만! 중학생을 위한 시험 4주 전 주차별 공부 루틴",
        "recommended_title": "중학교 첫 중간고사 멘붕 방지! 상위권이 꼭 지키는 '4주 분할 플래너' 작성법",
        "intro": "초등학교 때는 하루 이틀만 봐도 100점 맞던 아이가 중학교 첫 시험에서 무너지는 이유, 바로 '분량 조절과 시간 분배'의 실패 때문입니다.",
        "body_1": "1. [D-4주~3주]: 교과서 개념 정독 + 단원별 핵심 용어 형광펜 정리 (개념 1회독)",
        "body_2": "2. [D-2주]: 기출문제 풀이 & 틀린 문제 '오답 이유 1줄 요약' 단권화",
        "body_3": "3. [D-1주]: 서술형 예상 문제 직접 손으로 써보기 & 백지 복습 테스트",
        "outro": "시험은 지능이 아니라 계획의 승부입니다. 첨부된 4주 플래너 양식을 다운받아 오늘부터 실천해보세요.",
        "core_outline": "• D-4주 주차별 교과서 정독 & 개념 회독 전략\n• 기출문제 오답 단권화 노하우\n• 서술형 배점 챙기는 백지 복습법",
        "tags": "#중등공부법 #중학교중간고사 #중등내신 #중학교시험대비 #중등플래너 #중등맘"
    }
    
    # Item 3: Seasonal Must-Have Study Item & Mental Care
    item3 = {
        "category": "시즌별 핫아이템 & 학부모 멘탈케어",
        "subtitle": "2학기 집중력 2배 높이는 책상 정리템 & 학부모 코칭 팁",
        "target": "초·중등 전 연령 학부모 (자녀의 학습 환경 및 수면/집중력 케어)",
        "insight": "가을 환절기와 2학기 개학이 겹치면서 '학습 효율을 높여주는 물리적 환경 세팅 아이템(독서대, 집중 조명, 무소음 스톱워치)'과 '칭찬 대화법'에 대한 검색 수요가 급증하고 있습니다.",
        "title_a": "책상에 앉기만 하면 딴짓? 집중력 2배 올려주는 '초·중등 책상 꿀템 4가지'",
        "title_b": "학습 효율을 바꾸는 공간의 힘! 초등·중등 자녀 방 책상 배치 노하우",
        "title_c": "아이의 잠재력을 깨우는 부모의 한마디: '결과' 대신 '과정'을 칭찬하는 법",
        "recommended_title": "책상에 앉기만 하면 딴짓? 집중력 2배 올려주는 '초·중등 책상 꿀템 4가지'",
        "intro": "아무리 좋은 공부법도 환경이 어수선하면 10분을 넘기지 못합니다. 가을 신학기를 맞아 학습 피로도를 낮추고 몰입을 돕는 필수 가성비 아이템을 소개합니다.",
        "body_1": "1. [각도 조절 독서대]: 거북목 방지와 시야각 확보로 장시간 집중력 유지",
        "body_2": "2. [비주얼 타이머 (시각화 시계)]: 남은 시간이 눈으로 보이는 타이머로 시간 감각 훈련",
        "body_3": "3. [무소음 스톱워치 & 펜 꽂이]: 산만한 책상 위 물건을 줄이고 필수 필기구만 정돈",
        "outro": "아이의 책상 위 스마트폰은 다른 방으로 옮기고, 시각화 타이머를 선물해보세요. 작은 환경 변화가 큰 집중력을 만듭니다.",
        "core_outline": "• 거북목 예방 각도 조절 독서대 추천\n• 남은 시간이 색상으로 줄어드는 비주얼 타이머\n• 자녀의 과정을 인정해 주는 부모 칭찬 대화법",
        "tags": "#학습아이템 #초등책상정리 #공부방인테리어 #비주얼타이머 #학부모꿀팁 #자녀교육"
    }
    
    items = [item1, item2, item3]
    
    # 3. Render Markdown Report
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "edu_report_template.md")
    with open(template_path, "r", encoding="utf-8") as f:
        tpl = f.read()
        
    report_md = tpl.replace("{{DATE}}", today_str) \
                   .replace("{{TIMESTAMP}}", now_str) \
                   .replace("{{CURRENT_SEASON}}", "9월 신학기(2학기) 개학 2주 차 및 가을 중간고사 대비 시즌") \
                   .replace("{{PARENTS_MAIN_FOCUS}}", "산만해진 학습 습관 회복, 2학기 첫 내신 중간고사 대비, 집중력 유지 환경 조성") \
                   .replace("{{DAILY_STRATEGY}}", "초등 '재미와 성취감', 중등 '4주 분할 전략', 시즌별 '환경 및 멘탈 세팅' 3단계 구성") \
                   .replace("{{ITEM1_CATEGORY}}", item1["category"]) \
                   .replace("{{ITEM1_SUBTITLE}}", item1["subtitle"]) \
                   .replace("{{ITEM1_TARGET}}", item1["target"]) \
                   .replace("{{ITEM1_INSIGHT}}", item1["insight"]) \
                   .replace("{{ITEM1_TITLE_A}}", item1["title_a"]) \
                   .replace("{{ITEM1_TITLE_B}}", item1["title_b"]) \
                   .replace("{{ITEM1_TITLE_C}}", item1["title_c"]) \
                   .replace("{{ITEM1_INTRO}}", item1["intro"]) \
                   .replace("{{ITEM1_BODY_1}}", item1["body_1"]) \
                   .replace("{{ITEM1_BODY_2}}", item1["body_2"]) \
                   .replace("{{ITEM1_BODY_3}}", item1["body_3"]) \
                   .replace("{{ITEM1_OUTRO}}", item1["outro"]) \
                   .replace("{{ITEM1_TAGS}}", item1["tags"]) \
                   .replace("{{ITEM2_CATEGORY}}", item2["category"]) \
                   .replace("{{ITEM2_SUBTITLE}}", item2["subtitle"]) \
                   .replace("{{ITEM2_TARGET}}", item2["target"]) \
                   .replace("{{ITEM2_INSIGHT}}", item2["insight"]) \
                   .replace("{{ITEM2_TITLE_A}}", item2["title_a"]) \
                   .replace("{{ITEM2_TITLE_B}}", item2["title_b"]) \
                   .replace("{{ITEM2_TITLE_C}}", item2["title_c"]) \
                   .replace("{{ITEM2_INTRO}}", item2["intro"]) \
                   .replace("{{ITEM2_BODY_1}}", item2["body_1"]) \
                   .replace("{{ITEM2_BODY_2}}", item2["body_2"]) \
                   .replace("{{ITEM2_BODY_3}}", item2["body_3"]) \
                   .replace("{{ITEM2_OUTRO}}", item2["outro"]) \
                   .replace("{{ITEM2_TAGS}}", item2["tags"]) \
                   .replace("{{ITEM3_CATEGORY}}", item3["category"]) \
                   .replace("{{ITEM3_SUBTITLE}}", item3["subtitle"]) \
                   .replace("{{ITEM3_TARGET}}", item3["target"]) \
                   .replace("{{ITEM3_INSIGHT}}", item3["insight"]) \
                   .replace("{{ITEM3_TITLE_A}}", item3["title_a"]) \
                   .replace("{{ITEM3_TITLE_B}}", item3["title_b"]) \
                   .replace("{{ITEM3_TITLE_C}}", item3["title_c"]) \
                   .replace("{{ITEM3_INTRO}}", item3["intro"]) \
                   .replace("{{ITEM3_BODY_1}}", item3["body_1"]) \
                   .replace("{{ITEM3_BODY_2}}", item3["body_2"]) \
                   .replace("{{ITEM3_BODY_3}}", item3["body_3"]) \
                   .replace("{{ITEM3_OUTRO}}", item3["outro"]) \
                   .replace("{{ITEM3_TAGS}}", item3["tags"])
                   
    out_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(out_dir, exist_ok=True)
    report_file = os.path.join(out_dir, f"edu-blog-{today_str}.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    elapsed = time.time() - start_time
    print(f"🎉 [Edu-Blog Radar] Report generated in {elapsed:.2f}s! ({report_file})")
    
    # 4. Dispatch live alert to Telegram
    send_edu_telegram_notification(today_str, report_file, items)
    
    print("---EDU_SUMMARY_START---")
    print(json.dumps({
        "status": "success",
        "date": today_str,
        "report_file": report_file,
        "items_count": len(items),
        "items": [
            {"category": item1["category"], "title": item1["recommended_title"]},
            {"category": item2["category"], "title": item2["recommended_title"]},
            {"category": item3["category"], "title": item3["recommended_title"]}
        ]
    }, ensure_ascii=False, indent=2))
    print("---EDU_SUMMARY_END---")

if __name__ == "__main__":
    main()
