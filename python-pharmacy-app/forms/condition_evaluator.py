"""
Condition Evaluator - Evaluate field visibility and logic conditions
"""
from typing import Any, Dict, List
from datetime import datetime
import re


class ConditionEvaluator:
    """Evaluate conditions for form field visibility and behavior"""
    
    @staticmethod
    def evaluate_condition(condition: Dict, form_data: Dict) -> bool:
        """
        Evaluate a single condition
        
        Condition format:
        {
            "fieldId": "field_name",
            "operator": "equals|notEquals|greaterThan|lessThan|contains|isEmpty|isNotEmpty",
            "value": value_to_compare
        }
        """
        field_id = condition.get("fieldId")
        operator = condition.get("operator")
        expected_value = condition.get("value")
        
        field_value = form_data.get(field_id)
        
        if operator == "equals":
            return field_value == expected_value
        
        elif operator == "notEquals":
            return field_value != expected_value
        
        elif operator == "greaterThan":
            try:
                return float(field_value) > float(expected_value)
            except (TypeError, ValueError):
                return False
        
        elif operator == "lessThan":
            try:
                return float(field_value) < float(expected_value)
            except (TypeError, ValueError):
                return False
        
        elif operator == "greaterThanOrEqual":
            try:
                return float(field_value) >= float(expected_value)
            except (TypeError, ValueError):
                return False
        
        elif operator == "lessThanOrEqual":
            try:
                return float(field_value) <= float(expected_value)
            except (TypeError, ValueError):
                return False
        
        elif operator == "contains":
            if isinstance(field_value, str):
                return expected_value in field_value
            elif isinstance(field_value, list):
                return expected_value in field_value
            return False
        
        elif operator == "notContains":
            if isinstance(field_value, str):
                return expected_value not in field_value
            elif isinstance(field_value, list):
                return expected_value not in field_value
            return False
        
        elif operator == "isEmpty":
            return field_value is None or field_value == "" or field_value == []
        
        elif operator == "isNotEmpty":
            return field_value is not None and field_value != "" and field_value != []
        
        elif operator == "in":
            # Check if field_value is in list of expected_value
            if isinstance(expected_value, list):
                return field_value in expected_value
            return False
        
        elif operator == "notIn":
            if isinstance(expected_value, list):
                return field_value not in expected_value
            return False
        
        elif operator == "startsWith":
            if isinstance(field_value, str):
                return field_value.startswith(str(expected_value))
            return False
        
        elif operator == "endsWith":
            if isinstance(field_value, str):
                return field_value.endswith(str(expected_value))
            return False
        
        elif operator == "matches":
            # Regex match
            try:
                return re.match(expected_value, str(field_value)) is not None
            except re.error:
                return False
        
        return False
    
    @staticmethod
    def evaluate_conditions(conditions: List[Dict], form_data: Dict, logic: str = "AND") -> bool:
        """
        Evaluate multiple conditions with AND/OR logic
        
        logic: "AND" (all must be true) or "OR" (at least one must be true)
        """
        if not conditions:
            return True
        
        if logic.upper() == "AND":
            return all(ConditionEvaluator.evaluate_condition(cond, form_data) for cond in conditions)
        elif logic.upper() == "OR":
            return any(ConditionEvaluator.evaluate_condition(cond, form_data) for cond in conditions)
        else:
            return False
    
    @staticmethod
    def get_visible_fields(form_definition: Dict, form_data: Dict) -> List[str]:
        """
        Get list of field IDs that should be visible based on current form data
        """
        visible_fields = []
        
        sections = form_definition.get("sections", [])
        for section in sections:
            questions = section.get("questions", [])
            for question in questions:
                field_id = question.get("id")
                
                # Check if field has visibility conditions
                visibility = question.get("visibility", {})
                
                if not visibility:
                    # No conditions, always visible
                    visible_fields.append(field_id)
                else:
                    conditions = visibility.get("conditions", [])
                    logic = visibility.get("logic", "AND")
                    
                    if ConditionEvaluator.evaluate_conditions(conditions, form_data, logic):
                        visible_fields.append(field_id)
        
        return visible_fields
    
    @staticmethod
    def evaluate_field_behavior(field_config: Dict, form_data: Dict) -> Dict:
        """
        Evaluate dynamic field behavior based on conditions
        
        Returns dict with field behavior modifications:
        {
            "disabled": bool,
            "readonly": bool,
            "required": bool,
            "hidden": bool
        }
        """
        behavior = {
            "disabled": field_config.get("disabled", False),
            "readonly": field_config.get("readonly", False),
            "required": field_config.get("required", False),
            "hidden": False
        }
        
        # Check visibility
        visibility = field_config.get("visibility", {})
        if visibility:
            conditions = visibility.get("conditions", [])
            logic = visibility.get("logic", "AND")
            
            if conditions and not ConditionEvaluator.evaluate_conditions(conditions, form_data, logic):
                behavior["hidden"] = True
        
        # Check disabling conditions
        disable_when = field_config.get("disableWhen", {})
        if disable_when:
            conditions = disable_when.get("conditions", [])
            logic = disable_when.get("logic", "AND")
            
            if conditions and ConditionEvaluator.evaluate_conditions(conditions, form_data, logic):
                behavior["disabled"] = True
        
        # Check readonly conditions
        readonly_when = field_config.get("readonlyWhen", {})
        if readonly_when:
            conditions = readonly_when.get("conditions", [])
            logic = readonly_when.get("logic", "AND")
            
            if conditions and ConditionEvaluator.evaluate_conditions(conditions, form_data, logic):
                behavior["readonly"] = True
        
        # Check required conditions
        required_when = field_config.get("requiredWhen", {})
        if required_when:
            conditions = required_when.get("conditions", [])
            logic = required_when.get("logic", "AND")
            
            if conditions and ConditionEvaluator.evaluate_conditions(conditions, form_data, logic):
                behavior["required"] = True
        
        return behavior
    
    @staticmethod
    def calculate_field_value(field_config: Dict, form_data: Dict) -> Any:
        """
        Calculate field value if it has a calculation expression
        
        Calculation format:
        {
            "type": "calculation",
            "expression": "field1 + field2"
        }
        """
        if field_config.get("type") != "calculation":
            return None
        
        expression = field_config.get("expression", "")
        
        try:
            # Replace field references with actual values
            calc_expr = expression
            
            # Find all field references (e.g., {fieldId})
            field_refs = re.findall(r'\{([^}]+)\}', expression)
            
            for ref in field_refs:
                value = form_data.get(ref, 0)
                # Convert to string for replacement
                calc_expr = calc_expr.replace(f"{{{ref}}}", str(value))
            
            # Evaluate the expression (use safe eval or custom parser)
            # For security, only allow basic math operations
            result = eval(calc_expr, {"__builtins__": {}}, {})
            return result
        
        except Exception as e:
            print(f"Error calculating field value: {e}")
            return None
    
    @staticmethod
    def get_field_options(field_config: Dict, form_data: Dict) -> List:
        """
        Get dynamic options for a select field based on conditions
        """
        options = field_config.get("options", [])
        
        # Check if options are dynamic
        dynamic = field_config.get("dynamicOptions")
        if dynamic:
            # This would connect to external data source or calculate based on form data
            # For now, return static options
            pass
        
        # Filter options based on conditions
        filtered_options = field_config.get("filteredOptions")
        if filtered_options:
            conditions = filtered_options.get("conditions", [])
            logic = filtered_options.get("logic", "AND")
            
            if ConditionEvaluator.evaluate_conditions(conditions, form_data, logic):
                options = filtered_options.get("options", options)
        
        return options
