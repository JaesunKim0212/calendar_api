import logging
from typing import Optional, List
from calendars.service import find_conflict_events, find_available_schedule, create_event, update_event, delete_events
from common.config import DEFAULT_CALENDAR_ID

logger = logging.getLogger(__name__)

def handle_calendar_request(service, actions):
    '''
    사용자의 일정 요청 전체를 처리하는 오케스트레이터(Orchestrator)

    1. 일정 생성: create_event
        단, 일정 충돌 있을 경우 
            1) 다른 시간으로 다시 일정 잡기: 사용자 쿼리 처음 받은 로직으로 이동 필요
            2) 현재 일정으로 변경(update)
                - event_id가 1개인 경우: update_event 함수 사용
                - event_id가 2개 이상인 경우: delete_event + create_event 함수 사용
    
    2. 일정 확인
        1) 비어 있는 시간 확인: find_available_schedule
        2) 1) 케이스 제외 일정 확인: find_conflict_events
                
    3. 일정 수정/변경: update_event

    4. 일정 삭제: delete_event
    '''
    calendar_id = DEFAULT_CALENDAR_ID

    results = []

    for i, action in enumerate(actions, start=1):
        print(f"{i}. {action}")
        category = action.get("category", None)
        title = action.get("calendar_info").get("title", None)
        start_time = action.get("calendar_info").get("start_time", None)
        end_time = action.get("calendar_info").get("end_time", None)
        location = action.get("calendar_info").get("location", None)
        attendees = action.get("calendar_info").get("attendees", [])
        schedule_check = action.get("calendar_info").get("schedule_check_info", None)
        logger.info(f"[route_intent] Result 정보: {title}, {category}, {start_time}, {end_time}\n")

        if not title or not start_time or not end_time:
            print("일정 생성에 필요한 정보가 부족합니다. 제목, 원하는 행동, 시작 시간, 종료 시간을 다시 확인해 주세요.")

        attendee_emails = [{"email": attendee.get("email")} for attendee in attendees if attendees]
    
        events = find_conflict_events(service, start_time, end_time, schedule_check, calendar_id)
        event_ids = [event['id'] for event in events if events]
        if events:
            print(f"이 기간과 겹치는 일정: {len(events)}건\n")
            for i, event in enumerate(events, start=1):
                print(f"[{i}] 일정 내용: {event.get('summary', '제목 없음')}\n    일정 시작: {event.get('start', {}).get('dateTime', None)}\n    일정 종료: {event.get('end', {}).get('dateTime', None)}\n")
        
        # 일정 생성
        if category == "create":
            if not events:
                logger.info(f"[handle_calendar_request: {category}] 일정을 추가합니다. \n")
                event = create_event(service, title, start_time, end_time, attendee_emails, location, calendar_id)    
                print(f"일정이 추가되었습니다. 아래 링크를 확인해 주세요.\n{event.get('htmlLink')}")
                return "created_new_schedule"

            print(f"확인 결과, 해당 시간에는 일정이 있습니다.\n")
            
            # 기존 이벤트 제시
            for idx, event in enumerate(events, start=1):
                existing_title = event.get("summary", "제목 없음")
                start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date"))
                end = event.get("end", {}).get("dateTime", event.get("end", {}).get("date"))
                print(f"{idx}. {existing_title} | {start} ~ {end}")

            count = 0

            while count < 3:
                response = input("\n다른 시간으로 다시 일정을 잡으려면 '1', 위의 일정(들) 대신 현재 일정으로의 변경을 원하면 '2'를 입력해 주세요.: ")
                count += 1

                if isinstance(response, (int, str)) and str(response) not in ['1', '2']:
                    print("\n1 또는 2로만 입력해 주시기 바랍니다.")
                    continue

                if isinstance(response, (int, str)) and str(response) == "1":
                    print("\n일정 생성을 취소합니다. 다른 시간으로 다시 요청해 주시기 바랍니다.\n")
                    return "needs_new_conversation"
                
                elif isinstance(response, (int, str)) and str(response) == "2":
                    if len(event_ids) == 1: 
                        event = update_event(service, event_ids, title, start_time, end_time, attendee_emails, location, calendar_id)
                        print(f"\n일정이 변경되었습니다. 아래 링크를 확인해 주세요.\n{event.get('htmlLink')}")
                        return "updated_successfully"
                    
                    delete_success = delete_events(service, events, calendar_id)
                    
                    if not delete_success:
                        print(f"\n기존 일정이 모두 삭제되지 않았습니다. 다시 한 번 시도해 주세요.\n")
                        return None
                
                    event = create_event(service, title, start_time, end_time, attendee_emails, location, calendar_id)
                    print(f"\n기존 일정을 삭제하고 말씀하신 일정으로 추가하였습니다. 아래 링크를 확인해 주세요.\n{event.get('htmlLink')}")
                    return "created_new_schedule"
            print("이 일정에 대한 추가 업무를 종료합니다. 다음에 다시 시도해 주세요.\n")

        elif category == "find_conflict_events":
            logger.info(f"[handle_calendar_request: {category}] 일정을 확인합니다. \n")
            events = find_conflict_events(service, start_time, end_time, schedule_check, calendar_id)
            print(f"해당 시간에 잡혀 있는 일정 목록입니다.\n")
            for i, event in enumerate(events, start=1):
                print(f"    {i}) 일정 내용: {event['summary']}\n\t일정 시작: {event.get('start', {}).get('dateTime', None)}\n\t일정 종료: {event.get('end', {}).get('dateTime', None)}\n")
                logger.info(f"\n{i}) 일정 내용: {event['summary']}\n\t일정 시작: {event.get('start', {}).get('dateTime', None)}\n\t일정 종료: {event.get('end', {}).get('dateTime', None)}")
            return "checked_events"
        
        elif category == "find_available_schedule":
            logger.info(f"[handle_calendar_request: {category}] 일정을 확인합니다. \n")
            free_slots = find_available_schedule(service, start_time, end_time, calendar_id)
            print(f"요청하신 기간 내에 비어 있는 시간입니다.\n")
            for i, slot in enumerate(free_slots, start=1):
                print(f"    {i}) {slot.get('start')} ~ {slot.get('end')}")
            return "checked_available_schedule"
        
        elif category == "update":
            logger.info(f"[handle_calendar_request: {category}] 일정을 변경합니다. \n")
            event = update_event(service, event_ids, title, start_time, end_time, attendee_emails, location, calendar_id)
            print(f"일정이 변경되었습니다. 아래 링크를 확인해 주세요.\n{event.get('htmlLink')}")
            return "updated_successfully"
        
        elif category == "delete":
            logger.info(f"[handle_calendar_request: {category}] 일정을 삭제합니다. \n")
            if events:
                for event in events:
                    print(f"해당 시간에 잡혀있는 일정 목록입니다. 아래 목록을 삭제하시겠습니까?\n")
                    print(f"일정 내용: {event.get("summary", "제목 없음")}\n일정 시작 시간:{event.get("start", {}).get("dateTime")}\n일정 종료 시간: {event.get("end", {}).get("dateTime")}\n일정 링크: {event.get("htmlLink")}\n")
                response = input("삭제를 원하시면 'Y/y' 또는 '네', 원치 않으시면 'N/n/No/no' or '아니요'로 답변해 주세요.: ")
                if response in ["Y", "y", "네", "예"]:
                    if delete_events(service, events, calendar_id):
                        print(f"해당 일정이 삭제되었습니다. 캘린더를 확인해 주세요.\n")
                        return "deleted_successfully"
                else:
                    print(f"삭제가 진행되지 않았습니다. 다시 일정을 선택해 주세요.\n")
                    return "needs_new_conversation"
            else:
                print("해당 일자에 삭제할 일정이 없습니다. 요청한 내용을 다시 한 번 확인해 주세요.\n")
    
    return results
