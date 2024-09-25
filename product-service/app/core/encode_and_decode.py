import json 
from uuid import UUID 
from datetime import datetime

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj,datetime):
            return str(obj)
        return super().default(obj)
    
def custom_decoder(obj):
    for key, value in obj.items():
        # Check and convert UUID
        if isinstance(value, str):
            try:
                obj[key] = UUID(value)
            except (ValueError, TypeError):
                pass
        
        # Check and convert datetime
        if isinstance(value, str):
            try:
                obj[key] = datetime.fromisoformat(value)
            except (ValueError, TypeError):
                pass
    
    return obj