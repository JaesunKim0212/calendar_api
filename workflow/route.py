import logging
from calendars.handler import handle_calendar_request
# from gmail.auth import gmail_api
from common.config import DEFAULT_CALENDAR_ID

logger = logging.getLogger(__name__)

def route_intent(result, service):
    """
    의도를 구분하여 일정 관련 내용을 처리하도록 라우팅하는 함수

    Args:
        result (json): llm을 통해 생성된 calendar 정보
        service: google api를 통해 생성한 calendar 객체
    """
    if result.get('intent') == 'calendar':
        logger.info("[route_intent] calendar 업무로 확인되어 일정 업무를 시작합니다. 잠시만 기다려 주세요!\n")
        event = handle_calendar_request(service, result["actions"])
        if event == "created_new_schedule" or event == "updated_successfully":
            # gmail_service
            pass

        if event is not None and event != "needs_new_conversation":
            print(f"\n또 다른 일정을 관리/확인하고 싶으시면 다른 스케줄링 작업을 요청해 주세요.\n\n")
    else:
        print("저에게 주신 요청은 일정 관리 내용이 아니네요.\n저에게 일정 관련 내용을 알려 주시면 제가 캘린더 작업을 대신 진행할게요!\n전 당신의 일정 관리 Agent 입니다!\n")
