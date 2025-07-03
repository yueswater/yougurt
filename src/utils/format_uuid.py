from typing import Union
from uuid import UUID


def format_uuid(id: Union[str, UUID]) -> UUID:
    if isinstance(id, str):
        return UUID(id)
    return id
