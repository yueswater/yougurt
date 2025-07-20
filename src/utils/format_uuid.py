from uuid import UUID


def format_uuid(id):
    try:
        return UUID(str(id))
    except (ValueError, TypeError):
        return None
