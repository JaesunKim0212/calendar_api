from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TOKEN_PATH = PROJECT_ROOT / "token.json"
CREDENTIALS_PATH = PROJECT_ROOT / "credentials.json"
INTENT_PROMPT_PATH = PROJECT_ROOT / "prompts" / "intent_prompt.md"
DEFAULT_CALENDAR_ID = "primary"
TIMEZONE = "Asia/Seoul"
DEFAULT_ATTENDEES = [
    {
        "email": "jseang0212@gmail.com"
    }
]