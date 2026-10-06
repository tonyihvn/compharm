"""
Form and data validators
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator, EmailStr


class ClientValidationModel(BaseModel):
    """Validate client data"""
    pepfar_id: str
    full_name: str
    date_of_birth: Optional[datetime]
    gender: str
    phone_number: Optional[str]
    email: Optional[EmailStr]
    facility_id: str
    pharmacy_id: str
    
    @validator('pepfar_id')
    def validate_pepfar_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('PEPFAR ID must be at least 3 characters')
        return v.upper()
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or len(v) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()
    
    @validator('gender')
    def validate_gender(cls, v):
        if v.upper() not in ['M', 'F', 'O', 'MALE', 'FEMALE', 'OTHER']:
            raise ValueError('Gender must be M, F, or O')
        return v.upper()
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s\-\(\)]{10,}$', v):
            raise ValueError('Invalid phone number format')
        return v


class FormSubmissionValidator(BaseModel):
    """Validate form submission data"""
    form_id: int
    client_id: int
    data: Dict[str, Any]
    status: str = 'draft'
    
    @validator('data')
    def validate_data(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Form data must be a dictionary')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['draft', 'submitted', 'synced', 'rejected']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Accept various phone formats
    pattern = r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$'
    return re.match(pattern, phone) is not None


def validate_date_format(date_str: str, format: str = '%Y-%m-%d') -> bool:
    """Validate date string format"""
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_json_form(form_definition: Dict) -> List[str]:
    """Validate OpenMRS JSON form definition"""
    errors = []
    
    # Check required fields
    required_fields = ['name', 'pages', 'uuid']
    for field in required_fields:
        if field not in form_definition:
            errors.append(f'Missing required field: {field}')
    
    # Validate pages structure
    if 'pages' in form_definition and not isinstance(form_definition['pages'], list):
        errors.append('Pages must be an array')
    
    # Validate sections within pages
    if 'pages' in form_definition:
        for page in form_definition['pages']:
            if 'sections' not in page:
                errors.append('Each page must have sections')
    
    return errors
