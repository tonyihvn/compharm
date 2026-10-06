"""
Form Validators - Validate form field inputs
"""
from typing import Any, Dict, List
from datetime import datetime
import re


class FormValidator:
    """Validate form field data"""
    
    @staticmethod
    def validate_required(value: Any) -> bool:
        """Check if value is not empty"""
        return value is not None and value != "" and value != []
    
    @staticmethod
    def validate_text(value: str, min_length: int = 0, max_length: int = None) -> bool:
        """Validate text field"""
        if not isinstance(value, str):
            return False
        
        if len(value) < min_length:
            return False
        
        if max_length and len(value) > max_length:
            return False
        
        return True
    
    @staticmethod
    def validate_email(value: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, value) is not None
    
    @staticmethod
    def validate_phone(value: str, country_code: str = "ZA") -> bool:
        """Validate phone number"""
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]+', '', value)
        
        # South Africa format (example)
        if country_code == "ZA":
            # Allow +27, 0027, or 027 prefix, followed by 9 digits
            pattern = r'^(\+27|0027|027)?[0-9]{9}$'
            return re.match(pattern, cleaned) is not None
        
        # Generic validation - at least 7 digits
        return len(re.sub(r'[^0-9]', '', cleaned)) >= 7
    
    @staticmethod
    def validate_number(value: Any, min_val: float = None, max_val: float = None) -> bool:
        """Validate numeric field"""
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                return False
            if max_val is not None and num > max_val:
                return False
            return True
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def validate_date(value: str, format: str = "%Y-%m-%d") -> bool:
        """Validate date format"""
        try:
            datetime.strptime(value, format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_date_range(value: str, min_date: str = None, max_date: str = None) -> bool:
        """Validate date is within range"""
        try:
            date_obj = datetime.strptime(value, "%Y-%m-%d")
            
            if min_date:
                min_date_obj = datetime.strptime(min_date, "%Y-%m-%d")
                if date_obj < min_date_obj:
                    return False
            
            if max_date:
                max_date_obj = datetime.strptime(max_date, "%Y-%m-%d")
                if date_obj > max_date_obj:
                    return False
            
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_select(value: str, options: List[str]) -> bool:
        """Validate selected value is in options"""
        return value in options
    
    @staticmethod
    def validate_regex(value: str, pattern: str) -> bool:
        """Validate against regex pattern"""
        try:
            return re.match(pattern, value) is not None
        except re.error:
            return False
    
    @staticmethod
    def validate_field(field_config: Dict, value: Any) -> tuple[bool, str]:
        """
        Validate a field based on its configuration
        
        Returns: (is_valid, error_message)
        """
        if field_config.get("required") and not FormValidator.validate_required(value):
            return False, f"This field is required"
        
        if not value and not field_config.get("required"):
            return True, ""
        
        field_type = field_config.get("type", "text")
        
        if field_type == "text":
            if not FormValidator.validate_text(value, 
                field_config.get("minLength", 0),
                field_config.get("maxLength")):
                return False, "Invalid text format"
        
        elif field_type == "email":
            if not FormValidator.validate_email(value):
                return False, "Invalid email format"
        
        elif field_type == "phone":
            if not FormValidator.validate_phone(value):
                return False, "Invalid phone number"
        
        elif field_type == "number":
            if not FormValidator.validate_number(value,
                field_config.get("min"),
                field_config.get("max")):
                return False, f"Number must be between {field_config.get('min')} and {field_config.get('max')}"
        
        elif field_type == "date":
            if not FormValidator.validate_date(value):
                return False, "Invalid date format (use YYYY-MM-DD)"
            
            if not FormValidator.validate_date_range(value,
                field_config.get("minDate"),
                field_config.get("maxDate")):
                return False, "Date is outside allowed range"
        
        elif field_type == "select":
            if not FormValidator.validate_select(value, field_config.get("options", [])):
                return False, "Invalid selection"
        
        elif field_type == "regex":
            if not FormValidator.validate_regex(value, field_config.get("pattern", "")):
                return False, f"Invalid format: {field_config.get('message', 'Does not match pattern')}"
        
        return True, ""
    
    @staticmethod
    def validate_form(form_data: Dict, form_definition: Dict) -> tuple[bool, Dict[str, str]]:
        """
        Validate entire form
        
        Returns: (is_valid, errors_dict)
        """
        errors = {}
        
        sections = form_definition.get("sections", [])
        for section in sections:
            questions = section.get("questions", [])
            for question in questions:
                field_id = question.get("id")
                value = form_data.get(field_id)
                
                is_valid, error_msg = FormValidator.validate_field(question, value)
                if not is_valid:
                    errors[field_id] = error_msg
        
        return len(errors) == 0, errors
