import json
import logging
from string import Template
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from pathlib import Path
from openai import OpenAI
from common.config import INTENT_PROMPT_PATH

logger = logging.getLogger(__name__)

def get_datetime_context() -> dict:
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    print("week 체크: {now.weekday()}")
    monday = now - timedelta(days=now.weekday())
    friday = monday + timedelta(days=4)
    nextweek = monday + timedelta(days=7)
    monday_after_two_weeks = monday + timedelta(days=14)
    return {
        'today': now.strftime("%Y-%m-%d"),
        'monday': monday.date().isoformat(),
        'friday': friday.date().isoformat(),
        'nextweek_start': nextweek.date().isoformat(),
        'monday_after_two_weeks': monday_after_two_weeks.date().isoformat(),
        'year': now.year
    } 


def get_intent_prompt() -> str:
    prompt_path = INTENT_PROMPT_PATH
    with open(prompt_path, "r", encoding="UTF-8") as f:
        prompt = f.read()
    
    prompt = Template(prompt).safe_substitute(get_datetime_context())
    logger.info(f"[get_intent_prompt] Prompt conversion: {prompt}\n")
    return prompt

def grasp_intent(llm: OpenAI, user_query: str, sys_prompt: str) -> dict:
    """
    Grasp the intent of user query and get the grasped intent and formatted calendar info for API calling. 
    Args:
        user_query (str): user's input query
        sys_prompt (str): a prompt to provide LLM for understanding intent and get the result

    Returns:
        dict: dictionary format result
    """
    try:
        response = llm.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_query}
            ]
        )
    except Exception as e:
        print(f"Error generating the result: {e}")
        return {"intent": "", "error": str(e), "actions": []}
    
    output = response.choices[0].message.content
    logger.info(f"\n[grasp_intent] LLM Result: {output}\n")
    try:
        result = json.loads(output)
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        logger.info(f"JSON error: {e}")
        return {"intent": "", "error": str(e), "raw_output": output}

    return result