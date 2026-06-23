
# 1. Project overview

    - 이 프로젝트는 LLM 기반 Google calendar의 일정을 처리하는 Calendar Agent입니다. 

    - 사용자의 자연어 입력을 분석하여 아래의 업무들을 수행합니다. 
        - 일정 조회
        - 일정 생성
        - 일정 수정
        - 일정 삭제
    
    - Google Calendar API와 연동되며, 다중 일정 작업(Multi Action)도 지원합니다. 


# 2. Features

    - Natural language calendar scheduling
    - Create event
    - Check event
    - Update event
    - Delete event
    - Multi-step Planning
    - Confict detection
    - Google Calendar Invitation


# 3. Project Structure


    project/
        ├── calendars/
        │   ├── auth.py
        │   ├── handler.py
        │   └── service.py
        │
        ├── workflow/
        │   ├── planner.py
        │   └── router.py
        │
        ├── prompts/
        │   └── intent_prompt.md
        │
        ├── common/
        │   ├── logger.py
        │   └── config.py
        │
        ├── logs/
        │
        ├── main.py
        ├── README.md
        └── pyproject.toml



    [Workflow]

        Planner

        ↓

        Router

        ↓

        Calendar Handler

        ↓

        Google Calendar API


# 4. Tech stack

    - Python 3.12
    - OpenAI GPT-4o-mini
    - Google Calendar API
    - OAuth2
    - dotenv


# 5. Installation

    git clone https://github.com/JaesunKim0212/calendar_api.git



# 6. Environment Variables

    OPENAI_API_KEY="your openai api key"
    TOKEN_PATH="... / token.json"
    GOOGLE_CREDENTIALS="... / credential.json"

    - credentials.json은 Google Cloud Console에서 다운받아야 합니다. 



# 7. How to Run

    python main.py



# 8. Example

    1) 6월 23일 잡힌 회의 일정 삭제 해 줘
        - Planner Output: {
            "user_query": "6월 23일 잡힌 회의 일정 삭제 해 줘",
            "intent": "calendar",
            "actions": [
                { 
                    "category": "delete",
                    "calendar_info": 
                        {"title": "회의",
                        "location": null,
                        "start_time": "2026-06-23T00:00:00+09:00", 
                        "end_time": "2026-06-23T23:59:00+09:00",  
                        "timezone": "Asia/Seoul",
                        "attendees": []
                        }
                    }
                ]
            }
        - 결과: 해당 시간에 잡혀있는 일정 목록입니다. 아래 목록을 삭제하시겠습니까?
                삭제를 원하시면 'Y/y' 또는 '네', 원치 않으시면 'N/n/No/no' or '아니요'로 답변해 주세요.:
                해당 일정이 삭제되었습니다. 캘린더를 확인해 주세요.



# 9. Architecture

    User query -> Planner(LLM) -> Structured output -> Router -> Calendar Service -> Google Calendar 


# 10. Future Work

    - Gmail notification
    - Slack Notification
    - Google Contacts Integration
    - LangGraph Migration
    - Memory
    - Reflection
    - Logging/Fallback



# 11. Design Decisions

    ### Why Planner / Router / Handler?

    - Planner는 자연어 쿼리를 받아 의도를 분류하고 Structured Output으로 변환한다. 

    - Router는 Intent를 기반으로 Calendar Handler를 호출한다.

    - Handler는 Business Logic(사용자의 일정 요청)을 수행한다. 


    1) Calendar 처리 Agent 작업 흐름

    1. CLI로 입력받기
    2. LLM이 의도 판단 → "calendar"
    3. LLM이 schema에 맞게 날짜/시간/제목 등 추출
    4. 로직이 그걸 받아서 Google Calendar API 호출 전에 — 기존 일정 조회 먼저
    5. 충돌 없으면 등록, 있으면 알림


    2) Slack bot AI 관련 추천 논문 정보 게시 Agent 작업 흐름 및 구조


