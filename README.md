
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
    - Create/Check(find available schedules or find conflict events)/Update/Delete events
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

        Planner             : 자연어 쿼리를 받아 의도를 분류하고 Structured Output으로 변환

        ↓

        Router              : Intent 기반으로 Calendar Handler 호출

        ↓

        Calendar Handler    : Business Logic(사용자의 일정 요청) 수행

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
        - Planner Output: 
        {
    "user_query": "user query content",
    "intent": "calendar" or "",
    "actions": [
        { 
            "category": "find_available_schedule" or "find_conflict_events" or "create" or "update" or "delete",
            "calendar_info": 
                {"title": "치과 예약",
                "location": "서울특별시 강동구 암사동",
                "start_time": "2026-06-17T15:30:00+09:00", 
                "end_time": "2026-06-17T16:30:00+09:00",  
                "timezone": "Asia/Seoul",
                "attendees": [
                    {
                        "name": "김철수",
                        "email": "cjftnkim@gmail.com"
                    },
                ],
                "schedule_check_info": {
                    "keyword": ["예약", "치과"],
                    "attendee": ["cjftnkim@gmail.com"],
                    "location": "암사동"
                    } 
                }
            }
        ]
        - 결과: 해당 시간에 잡혀있는 일정 목록입니다. 아래 목록을 삭제하시겠습니까?
                삭제를 원하시면 'Y/y' 또는 '네', 원치 않으시면 'N/n/No/no' or '아니요'로 답변해 주세요.: y
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
    - Fallback

