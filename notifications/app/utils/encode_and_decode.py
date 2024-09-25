import json
from uuid import UUID
from datetime import datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (UUID, datetime)):
            return str(obj)
        return super().default(obj)

def custom_decoder(obj):
    for key, value in obj.items():
        if isinstance(value, str):
            obj[key] = _try_convert_to_uuid_or_datetime(value)
    return obj

def _try_convert_to_uuid_or_datetime(value):
    """Attempt to convert a string to a UUID or datetime, returning the original value if unsuccessful."""
    try:
        return UUID(value)
    except (ValueError, TypeError):
        pass
    
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return value
