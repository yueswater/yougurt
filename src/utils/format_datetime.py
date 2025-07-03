from datetime import datetime
from typing import Union


def format_datetime(time: Union[str, datetime]):
    if isinstance(time, str):
        return datetime.fromisoformat(time)
    return time
