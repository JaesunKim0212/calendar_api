import logging
from pathlib import Path
from datetime import datetime

Path("logs").mkdir(exist_ok=True)

today = datetime.now().strftime("%Y%m%d")

def setup_logger():
    logging.basicConfig(filename=f"logs/calendar.{today}.log", 
                            filemode="a", 
                            format=("%(asctime)s %(levelname)s | "
                                    "%(name)s:%(lineno)d | "
                                    "%(message)s"
                                    ),
                            datefmt="[%Y.%m.%d %H:%M:%S]",
                            level=logging.INFO)
