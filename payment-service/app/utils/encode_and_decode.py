import json
from uuid import UUID
from datetime import datetime
from app.models.payment_model import PaymentMethod

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON Encoder that handles UUID, datetime, and PaymentMethod objects."""
    
    def default(self, obj):
        if isinstance(obj, UUID):
            # Convert UUID to string
            return str(obj)
        
        if isinstance(obj, datetime):
            # Convert datetime to string (ISO format)
            return obj.isoformat()
        
        if isinstance(obj, PaymentMethod):
            # Convert PaymentMethod to dictionary representation
            return obj.dict()
        
        # Use default behavior for other types
        return super().default(obj)

def custom_decoder(obj):
    """Custom JSON Decoder that converts strings to UUID and datetime objects where applicable."""
    
    for key, value in obj.items():
        if isinstance(value, str):
            # Attempt to convert to UUID
            try:
                obj[key] = UUID(value)
            except (ValueError, TypeError):
                pass
            
            # Attempt to convert to datetime (ISO format)
            try:
                obj[key] = datetime.fromisoformat(value)
            except (ValueError, TypeError):
                pass
    
    return obj
