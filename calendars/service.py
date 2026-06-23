import logging
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from common.config import DEFAULT_CALENDAR_ID, TIMEZONE, DEFAULT_ATTENDEES

logger = logging.getLogger(__name__)

def create_event(service, title: str, start_time: str, end_time: str, attendee_emails: List[dict], location: Optional[str] = None, calendar_id: str=DEFAULT_CALENDAR_ID):
    attendees = DEFAULT_ATTENDEES.copy()
    print(f"default 참여자: {attendees}\n")
    if attendee_emails:
        attendee_emails = [
            email_info 
            for email_info in attendee_emails
            if email_info.get('email')
        ]
        attendees.extend(attendee_emails)
        print(f"참석자 메일주소: {attendees}\n")
    event_body = {
        "summary": title,
        "start": {
            "dateTime": start_time,
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": end_time,
            "timeZone": TIMEZONE,
        },
        "attendees": attendees
    }
    
    if location:
        event_body["location"] = location

    event = service.events().insert(calendarId=calendar_id, body=event_body, sendUpdates="all").execute()
    return event


def find_conflict_events(service, start_time: str, end_time: str, schedule_info: Optional[dict]=None, calendar_id: str=DEFAULT_CALENDAR_ID):
    """
    특정 키워드(장소, 제목, 참석자) 정보를 기반으로 event 탐색 및 반환하는 함수
    """

    params = {
        "calendarId": calendar_id,
        "timeMin": start_time,
        "timeMax": end_time,
        "singleEvents": True,
        "orderBy": "startTime"
    }

    events = service.events().list(**params).execute().get("items", [])
    
    if schedule_info:
        keywords = schedule_info.get('keyword', None)
        location = schedule_info.get('location', None)
        attendant_email = schedule_info.get('attendee', None)


        # 특정 키워드 포함된 이벤트 필터
        if keywords:
            events = [
                        e for e in events
                        if any(kw in e.get("summary", "") for kw in keywords)
                    ]


        # 특정 참석자 포함된 경우 이벤트 필터
        if attendant_email:
            if len(attendant_email) == 1:
                events = [
                            e for e in events
                            if any(attendant['email'] == f"{attendant_email}"
                            for attendant in e.get("attendees", []))
                    ] 
            elif len(attendant_email) > 1:
                pass
                '''
                events_ = []
                for email in attendant_email:
                    events_.append([e for e in events if any(attendant['email'] == f"{email}")
                                    for attendant in e.get("attendees", [])])
                events = list(set(events_))
                '''
                
        # 위치가 포함된 경우 이벤트 필터
        if location:
            events = [
                        e for e in events
                        if location in (e.get('location') or '')
                    ]

    return events


def find_available_schedule(service, start_time: str, end_time: str, calendar_id: str=DEFAULT_CALENDAR_ID):
    KST = ZoneInfo("Asia/Seoul")

    body = {
        "timeMin": start_time,
        "timeMax": end_time,
        "timeZone": "Asia/Seoul",
        "items": [{"id": calendar_id}]
    }

    result = service.freebusy().query(body=body).execute()
    busy_times = result["calendars"][calendar_id]["busy"]

    free_slots = []
    cursor = datetime.fromisoformat(start_time).astimezone(KST)

    for busy in busy_times:
        busy_start = datetime.fromisoformat(
            busy["start"].replace("Z", "+00:00")
            ).astimezone(KST)
        # logger.info(f'busy_start: {busy_start} | Type: {type(busy_start)}')
        busy_end = datetime.fromisoformat(
            busy["end"].replace("Z", "+00:00")
            ).astimezone(KST)
        # logger.info(f'busy_end: {busy_end} | Type: {type(busy_end)}')
        if cursor < busy_start:
            free_slots.append({"start": cursor, "end": busy_start})
        cursor = max(cursor, busy_end)

    end_time_ = datetime.fromisoformat(end_time).astimezone(KST)
    if cursor < end_time_:
        free_slots.append({"start": cursor, "end":end_time_})

    return free_slots


def update_event(service, event_ids: List[str], title: str, start_time: str, end_time: str, attendee_emails: List[dict], location: Optional[str]=None, calendar_id: str=DEFAULT_CALENDAR_ID):
    if len(event_ids) != 1:
        print(f"이벤트 ID가 1개가 아니어서 일정을 변경할 수 없습니다. 기존 일정을 확인해 주세요.\n")
        return None
    
    attendees = DEFAULT_ATTENDEES.copy()
    if attendee_emails:
        attendee_emails = [
            email_info 
            for email_info in attendee_emails
            if email_info.get('email')
        ]
    attendees.extend(attendee_emails)
    event_id = event_ids[0]
    event_body = {
        "summary": title,
        "start": {
            "dateTime": start_time,
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": end_time,
            "timeZone": TIMEZONE,
        },
        "attendees": attendees
    }

    if location:
        event_body["location"] = location

    updated_event = service.events().update(
                                calendarId=calendar_id, 
                                eventId=event_id,
                                body=event_body,
                                sendUpdates="all"
                                ).execute()

    return  updated_event


def delete_events(service, events: list[dict], calendar_id: str=DEFAULT_CALENDAR_ID) -> bool:
    try:
        for event in events:
            service.events().delete(
                calendarId=calendar_id,
                eventId=event["id"]
            ).execute()
        return "deleted_successfully"
    except Exception as e:
        print(f"일정 삭제 중 오류 발생: {e}")
        return "fail to delete"