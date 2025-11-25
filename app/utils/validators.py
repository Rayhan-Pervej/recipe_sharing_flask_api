import re
from typing import Dict, List, Optional

def validate_email(email:str) -> bool:

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password:str) -> Dict[str, List[str]]:

    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_username(username: str) -> Dict[str, List[str]]:
    errors = []
    if len(username) < 3:
        errors.append("Username must be at least 3 characters long")
    
    if len(username) > 80:
        errors.append("Username must not exceed 80 characters")
    
    if not re.match(r'^[a-zA-Z]', username):
        errors.append("Username must start with a letter")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        errors.append("Username can only contain letters, numbers, underscores, and hyphens")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_required_fields(data: Dict, required_fields: List[str])-> Dict[str, List[str]]:
    errors = {}
    
    for field in required_fields:
        if field not in data:
            errors[field] = [f"{field} is required"]
        elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            errors[field] = [f"{field} cannot be empty"]
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def validate_rating_score(score: int) -> bool:
    return isinstance(score, int) and 1 <= score <= 5