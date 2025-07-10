from datetime import datetime
from typing import Union


def format_datetime(time: Union[str, datetime]):
    if isinstance(time, str):
        try:
            return datetime.fromisoformat(time)
        except ValueError:
            return datetime.strptime(time, "%Y-%m-%d")
    return time


def format_date_only(time: Union[str, datetime]) -> str:
    dt = format_datetime(time)
    return dt.strftime("%Y-%m-%d")
