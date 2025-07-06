import os
import time
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import winsound

# ====== .env 로드 ======
print(">> 환경 변수 로드 중...")
load_dotenv()
GEMINI_API_KEY = os.getenv("geminiKey")

# ====== Gemini 클라이언트 설정 ======
print(">> Gemini API 설정 중...")
genai.configure(api_key=GEMINI_API_KEY)

# ====== 파일 설정 ======
TOPIC_LOG_FILE = "topics.txt"
LOG_FILE = f"debate_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
MAX_TURNS = 9

# ====== 파일 I/O ======
def append_to_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n\n")

def get_previous_topics():
    try:
        with open(TOPIC_LOG_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def save_new_topic(topic):
    with open(TOPIC_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(topic + "\n")

# ====== 주제 생성 ======
def generate_new_topic(previous_topics):
    topic_list = "\n".join(f"- {t}" for t in previous_topics)
    prompt = f"""다음은 지금까지 사용된 주제입니다:

{topic_list}
이 주제들과 겹치지 않도록, 흥미롭고 신선한 과학 또는 기술 관련 주제를 하나만 제시해 주세요.  
**주제만 간결하게 출력해 주세요. 설명, 이유, 분석은 하지 마세요.**
"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# ====== 프롬프트 생성 ======
def build_prompt(topic, log, last_message, speaker, turn):
    partner = "Ash 님" if speaker == "Taylor 님" else "Taylor 님"
    tone_hint = ""
    if speaker == "Taylor 님":
        tone_hint = "당신은 감성적이고 공감력 있는 스타일입니다."
        winsound.Beep(1200, 400)  # 높은 삡 (1200Hz, 200ms)
    else:
        tone_hint = "당신은 논리적이고 분석적인 스타일입니다."
        winsound.Beep(600, 400)   # 낮은 삡 (600Hz, 200ms)

    closing_hint = ""
    if turn >= MAX_TURNS - 1:
        closing_hint = "이번이 마지막 발언입니다. 상대의 말을 간단히 받아주고, 대화를 정리하며 인사로 마무리해주세요."
    elif turn >= MAX_TURNS - 2:
        closing_hint = "이제 대화를 정리해나가야 할 시점입니다. 핵심을 요약하거나 결론을 시도해보세요."

    return f"""주제: {topic}

지금까지의 대화:
{log}

{partner}이 이렇게 말했습니다:
\"{last_message}\"

당신({speaker})은 자연스럽게 이어서 3문장 이내로 응답하세요.
{tone_hint}
{closing_hint}
상대의 의견에 짧게 반응하고, 질문하거나 생각을 물어보세요. 마지막에는 너무 딱딱하지 않게 자연스럽게 마무리하세요.

당신의 다음 말은?"""

# ====== Gemini 응답 ======
def call_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"!! Gemini 오류 발생: {e}")
        return f"[Gemini 오류: {e}]"

# ====== 메인 실행 ======
def main():
    print(">> 이전 주제 목록 불러오는 중...")
    previous_topics = get_previous_topics()

    print(">> 새로운 주제 생성 중...")
    topic = generate_new_topic(previous_topics)
    topic = "AGI 와 SGI 의 도래 시기 및 최신 뉴스"
    save_new_topic(topic)

    print(f"\n오늘의 대화 주제: {topic}")
    append_to_log(f"[주제] {topic}")

    last_message = "이 주제에 대해 이야기해볼까요?"

    for turn in range(MAX_TURNS):
        speaker = "Taylor 님" if turn % 2 == 0 else "Ash 님"
        print(f"\n== {turn+1}/{MAX_TURNS}턴 | {speaker} ==")

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log = f.read()

        prompt = build_prompt(topic, log, last_message, speaker, turn)
        
        print(">> Gemini 호출 중...")
        reply = call_gemini(prompt)

        append_to_log(f"{speaker}: {reply}")
        print(">> 응답 저장 완료")

        last_message = reply
        time.sleep(1)

    print("\n>> 모든 턴 종료. 대화 완료.")

if __name__ == "__main__":
    main()
