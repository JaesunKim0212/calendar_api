import os
import logging
from common.logger import setup_logger
from workflow.planner import get_intent_prompt, grasp_intent
from workflow.route import route_intent
from calendars.auth import calendar_api
# from gmail.auth import gmail_api6
from dotenv import load_dotenv
from openai import OpenAI
from common.config import TOKEN_PATH


load_dotenv()
setup_logger()
logger = logging.getLogger(__name__)
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    """
    1. Cli로 사용자 쿼리 입력
    2. 쿼리 + 프롬프트 LLM 제공, 호출 -> 의도 판단 
    3. 
        1) 답변이 'calendar'의 경우 structured_output google calendar api에 제공
        2) 답변이 'calendar'가 아닌 경우, 알림 제공
    4. calendar의 일정 확인
        1) 해당 일정에 시간이 비어있는 경우, 일정 추가 + 추가 성공 알림
        2) 해당 일정에 시간이 차있는 경우, 해당 일정은 이미 다른 일정으로 인해 추가가 불가하다는 알림 제공
    """
    
    logger.info("Starts to implement the Calendar Agent!")

    check_count = 0
    intent_system_prompt = get_intent_prompt()
    service = calendar_api(TOKEN_PATH)
    # gmail_service = gmail_api(TOKEN_PATH)

    while True:
        # Get a user query
        user_query = input("Hello, what can I help you?\n")
        print(f"If you want to quit chatting with me, please answer '끝', '종료', 'exit' or 'bye'.\n")
        if user_query.lower().strip() in ['끝', 'exit', 'bye', 'done', '종료']:
            print("다음에 또 질문해 주세요. 안녕!")
            logger.info("Finished!")
            break
        
        # If the query is too short, give the user another try to write a query correctly (max: 3 times)  
        if len(user_query.split(" ")) < 3:
            if check_count >= 3:
                print(f"이번 채팅은 종료합니다. 질문을 다시 한 번 확인하고 작성해 주세요!\n")
                logger.info("Finished!")
                break
            print(f"질문이 너무 짧습니다. 다시 한 번 질문을 적어주세요. [query: {user_query}]\n")
            check_count += 1
            continue
        
        logger.info(f"[grasp_intent] 사용자 요청에 대한 의도를 파악합니다.")
        result = grasp_intent(llm, user_query, intent_system_prompt)
        print(f"[grasp_intent] Result:\n{result}")
        route_intent(result, service)
        logger.info(f"[route_intent] 캘린더 업무를 완료했습니다.")


if __name__ == "__main__":
    main()