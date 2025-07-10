from datetime import datetime
from typing import Optional, Union


def format_datetime(time: Union[str, datetime, None]) -> Optional[datetime]:
    if not time or (isinstance(time, str) and time.strip() == ""):
        return None

    if isinstance(time, str):
        try:
            return datetime.fromisoformat(time)
        except ValueError:
            try:
                # e.g. "2025-07-10 00:00:01"
                return datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    return datetime.strptime(time, "%Y-%m-%d")
                except ValueError:
                    return None

    return time


def format_date_only(time: Union[str, datetime, None]) -> str:
    dt = format_datetime(time)
    return dt.strftime("%Y-%m-%d") if dt else ""
