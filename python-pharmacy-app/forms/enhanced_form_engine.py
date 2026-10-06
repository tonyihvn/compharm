"""Enhanced form engine for rendering and processing pharmacy forms."""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import jsonschema
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


class FieldType(str, Enum):
    """Supported field types."""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    DATETIME = "datetime"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    FILE_UPLOAD = "file"
    TABLE = "table"
    GROUP = "group"
    SECTION = "section"


class FormEngine:
    """Handles form rendering, validation, and processing."""

    def __init__(self, form_schema: Dict[str, Any]):
        """Initialize form engine with form schema."""
        self.form_schema = form_schema
        self.form_id = form_schema.get("uuid", form_schema.get("id"))
        self.form_name = form_schema.get("name", "Untitled Form")
        self.pages = form_schema.get("pages", [])
        self.validators = {}
        self._build_validators()

    def _build_validators(self):
        """Build validation rules from form schema."""
        for page in self.pages:
            sections = page.get("sections", [])
            for section in sections:
                questions = section.get("questions", [])
                for question in questions:
                    field_id = question.get("id")
                    if field_id:
                        self.validators[field_id] = self._build_field_validator(question)

    def _build_field_validator(self, field: Dict[str, Any]) -> Dict[str, Any]:
        """Build validation rules for a field."""
        validator = {
            "required": field.get("required", False),
            "type": field.get("type"),
            "field_type": field.get("questionOptions", {}).get("rendering", "text")
        }

        # Custom validators
        if "validators" in field:
            validator["custom_validators"] = field.get("validators", [])

        # Options for select/radio fields
        if "questionOptions" in field and "answers" in field["questionOptions"]:
            validator["options"] = [a.get("label") for a in field["questionOptions"]["answers"]]

        return validator

    def get_pages(self) -> List[Dict]:
        """Get all form pages."""
        return self.pages

    def get_page_by_label(self, label: str) -> Optional[Dict]:
        """Get a specific page by label."""
        for page in self.pages:
            if page.get("label") == label:
                return page
        return None

    def get_page_sections(self, page_index: int) -> List[Dict]:
        """Get sections for a specific page."""
        if 0 <= page_index < len(self.pages):
            return self.pages[page_index].get("sections", [])
        return []

    def get_section_questions(self, page_index: int, section_index: int) -> List[Dict]:
        """Get questions for a specific section."""
        sections = self.get_page_sections(page_index)
        if 0 <= section_index < len(sections):
            return sections[section_index].get("questions", [])
        return []

    def validate_form_data(self, form_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate complete form data."""
        errors = []

        for field_id, validator in self.validators.items():
            # Check required fields
            if validator.get("required") and field_id not in form_data:
                errors.append(f"{field_id}: This field is required")
            elif field_id in form_data:
                value = form_data[field_id]
                # Validate field value
                field_errors = self._validate_field_value(field_id, value, validator)
                errors.extend(field_errors)

        return len(errors) == 0, errors

    def _validate_field_value(self, field_id: str, value: Any, validator: Dict[str, Any]) -> List[str]:
        """Validate a single field value."""
        errors = []

        # Skip validation for empty optional fields
        if not value and not validator.get("required"):
            return errors

        field_type = validator.get("field_type", "text")

        # Type-specific validation
        if field_type == "number":
            if value and not isinstance(value, (int, float)):
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors.append(f"{field_id}: Must be a valid number")

        elif field_type == "date" or field_type == "datetime":
            if value and not self._is_valid_date(value):
                errors.append(f"{field_id}: Must be a valid date")

        elif field_type == "select" or field_type == "radio":
            options = validator.get("options", [])
            if options and value not in options:
                errors.append(f"{field_id}: Invalid selection")

        # Custom validators
        for custom_validator in validator.get("custom_validators", []):
            val_type = custom_validator.get("type")
            if val_type == "date":
                allow_future = custom_validator.get("allowFutureDates", True)
                if isinstance(allow_future, str):
                    allow_future = allow_future.lower() == "true"
                if not allow_future:
                    if self._is_future_date(value):
                        errors.append(f"{field_id}: Future dates are not allowed")

        return errors

    @staticmethod
    def _is_valid_date(value: Any) -> bool:
        """Check if value is a valid date."""
        if isinstance(value, datetime):
            return True
        if isinstance(value, str):
            date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"]
            for fmt in date_formats:
                try:
                    datetime.strptime(value, fmt)
                    return True
                except ValueError:
                    continue
        return False

    @staticmethod
    def _is_future_date(value: Any) -> bool:
        """Check if value is a future date."""
        try:
            if isinstance(value, str):
                date_formats = ["%Y-%m-%d", "%d-%m-%Y"]
                date_obj = None
                for fmt in date_formats:
                    try:
                        date_obj = datetime.strptime(value, fmt).date()
                        break
                    except ValueError:
                        continue
                if date_obj is None:
                    return False
            elif isinstance(value, datetime):
                date_obj = value.date()
            else:
                return False

            return date_obj > datetime.now().date()
        except Exception as e:
            logger.warning(f"Error checking future date: {str(e)}")
            return False

    def process_form_submission(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and format form submission data."""
        processed_data = {
            "form_id": self.form_id,
            "form_name": self.form_name,
            "submitted_at": datetime.utcnow().isoformat(),
            "form_data": {}
        }

        for field_id, value in form_data.items():
            # Skip empty values
            if value is None or value == "":
                continue

            processed_data["form_data"][field_id] = {
                "value": value,
                "submitted_at": datetime.utcnow().isoformat()
            }

        return processed_data

    def get_form_metadata(self) -> Dict[str, Any]:
        """Get form metadata."""
        return {
            "id": self.form_id,
            "name": self.form_name,
            "pages_count": len(self.pages),
            "created_at": self.form_schema.get("created_at"),
            "updated_at": self.form_schema.get("updated_at"),
            "processor": self.form_schema.get("processor", "EncounterFormProcessor"),
            "version": self.form_schema.get("version", 1)
        }

    def validate_conditional_logic(self, form_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate conditional field visibility and requirements."""
        visibility = {}

        for page in self.pages:
            for section in page.get("sections", []):
                for question in section.get("questions", []):
                    field_id = question.get("id")
                    if field_id:
                        # Check hide expressions
                        hide_expr = question.get("hide", False)
                        if isinstance(hide_expr, dict) and "hideWhenExpression" in hide_expr:
                            # Simplified expression evaluation
                            visibility[field_id] = True

        return visibility

    @staticmethod
    def extract_calculated_fields(questions: List[Dict]) -> Dict[str, str]:
        """Extract calculated fields from questions."""
        calculated = {}
        for question in questions:
            if question.get("type") == "control":
                field_id = question.get("id")
                calc_expr = question.get("questionOptions", {}).get("calculate", {})
                if calc_expr and field_id:
                    calculated[field_id] = calc_expr.get("calculateExpression", "")
        return calculated
