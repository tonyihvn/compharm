"""Form engine for rendering and validating OpenMRS JSON forms."""

import json
import logging
from typing import Dict, Any, List, Optional
from .validators import FormValidator
from .condition_evaluator import ConditionEvaluator

logger = logging.getLogger(__name__)


class FormEngine:
    """Engine for processing OpenMRS-style JSON forms."""

    def __init__(self):
        """Initialize form engine."""
        self.validator = FormValidator()
        self.condition_evaluator = ConditionEvaluator()

    def load_form(self, form_json: Dict[str, Any] or str) -> Dict[str, Any]:
        """Load and parse a form from JSON."""
        if isinstance(form_json, str):
            try:
                form_json = json.loads(form_json)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON form: {e}")
                raise ValueError(f"Invalid form JSON: {e}")
        
        # Validate form structure
        if not self._validate_form_structure(form_json):
            raise ValueError("Invalid form structure")
        
        return form_json

    def extract_questions(self, form: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all questions from a form."""
        questions = []
        
        if "pages" in form:
            for page in form["pages"]:
                if "sections" in page:
                    for section in page["sections"]:
                        if "questions" in section:
                            questions.extend(section["questions"])
        
        return questions

    def get_question_by_id(self, form: Dict[str, Any], question_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific question by ID."""
        questions = self.extract_questions(form)
        for question in questions:
            if question.get("id") == question_id:
                return question
        return None

    def evaluate_visibility(self, question: Dict[str, Any], form_data: Dict[str, Any]) -> bool:
        """Evaluate if a question should be visible based on conditions."""
        if "hide" not in question:
            return True
        
        hide_config = question["hide"]
        if "hideWhenExpression" in hide_config:
            expression = hide_config["hideWhenExpression"]
            return not self.condition_evaluator.evaluate(expression, form_data)
        
        return True

    def get_question_value(self, form_data: Dict[str, Any], question_id: str) -> Any:
        """Get the current value of a question from form data."""
        return form_data.get(question_id)

    def validate_question(self, question: Dict[str, Any], value: Any) -> tuple[bool, Optional[str]]:
        """Validate a question's value."""
        if value is None and question.get("required", False):
            return False, f"{question.get('label')} is required"
        
        if value is not None:
            errors = self.validator.validate_question(question, value)
            if errors:
                return False, errors[0]
        
        return True, None

    def validate_form(self, form: Dict[str, Any], form_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate all questions in a form."""
        questions = self.extract_questions(form)
        errors = []
        
        for question in questions:
            # Check if question should be validated (is visible)
            if not self.evaluate_visibility(question, form_data):
                continue
            
            question_id = question.get("id")
            value = form_data.get(question_id)
            
            is_valid, error_msg = self.validate_question(question, value)
            if not is_valid:
                errors.append(f"{error_msg}")
        
        return len(errors) == 0, errors

    def calculate_derived_values(self, form: Dict[str, Any], form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived field values based on expressions."""
        questions = self.extract_questions(form)
        calculated_values = {}
        
        for question in questions:
            if question.get("type") == "control" and "questionOptions" in question:
                options = question["questionOptions"]
                if "calculate" in options and "calculateExpression" in options["calculate"]:
                    # This would require async evaluation of API calls
                    # For now, we'll mark it for later processing
                    question_id = question.get("id")
                    calculated_values[question_id] = None
        
        return calculated_values

    def _validate_form_structure(self, form: Dict[str, Any]) -> bool:
        """Validate the basic structure of a form."""
        # Must have pages
        if "pages" not in form or not isinstance(form["pages"], list):
            return False
        
        # Each page must have sections
        for page in form["pages"]:
            if "sections" not in page or not isinstance(page["sections"], list):
                return False
            
            # Each section must have questions
            for section in page["sections"]:
                if "questions" not in section or not isinstance(section["questions"], list):
                    return False
        
        return True

    def get_form_metadata(self, form: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from form."""
        return {
            "name": form.get("name"),
            "uuid": form.get("uuid"),
            "version": form.get("version"),
            "processor": form.get("processor"),
            "encounter_type": form.get("encounterType"),
            "published": form.get("published", False),
            "retired": form.get("retired", False)
        }
