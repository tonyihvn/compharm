# OpenMRS O3 Ampath Forms - Quick Reference Guide

## Overview
OpenMRS O3 uses Ampath form definitions - JSON structures that define dynamic, interactive forms for healthcare data collection. These forms support complex validation, conditional visibility, and dynamic calculations.

---

## Form Structure Hierarchy

```
Form (root)
├── name: string (form title)
├── uuid: string (unique identifier)
├── processor: string ("EncounterFormProcessor", "ObsFormProcessor", etc.)
├── pages: Array of Pages
│   └── Page
│       ├── label: string (page title)
│       ├── sections: Array of Sections
│       │   └── Section
│       │       ├── label: string (section title)
│       │       ├── questions: Array of Questions
│       │       │   └── Question
│       │       │       ├── id: string (unique field identifier)
│       │       │       ├── type: string (question/control type)
│       │       │       ├── label: string (display label)
│       │       │       ├── questionOptions: Object (rendering & behavior)
│       │       │       ├── required: boolean
│       │       │       ├── validators: Array (validation rules)
│       │       │       ├── hide: Object (conditional visibility)
│       │       │       └── ...other properties
```

---

## Key Form Properties

### Question Properties

| Property | Type | Purpose | Example |
|----------|------|---------|---------|
| `id` | string | Unique identifier for field | `"visitDate"` |
| `label` | string | Display name for field | `"Visit Date"` |
| `type` | string | Field type (question/control) | `"encounterDatetime"`, `"obs"` |
| `required` | boolean | Field is mandatory | `true` |
| `readonly` | boolean | Field cannot be edited | `false` |
| `hide` | object | Conditional visibility rules | `{ "hideWhenExpression": "..."}` |

### Question Options (questionOptions)

Controls how the field is rendered and behaves:

```json
{
  "rendering": "date|number|text|checkbox|radio|select|textarea",
  "concept": "CONCEPT_UUID",
  "rows": 3,
  "max": 100,
  "min": 0,
  "calculate": {
    "calculateExpression": "javascript expression"
  }
}
```

### Common Question Types

```javascript
{
  // Encounter DateTime - Visit date/time
  "type": "encounterDatetime",
  "questionOptions": { "rendering": "date" }
},
{
  // Observation value - Weight, height, etc.
  "type": "obs",
  "questionOptions": {
    "concept": "5089AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", // Weight concept UUID
    "rendering": "number"
  }
},
{
  // Calculated field - BMI, etc.
  "type": "control",
  "questionOptions": {
    "rendering": "number",
    "calculate": {
      "calculateExpression": "fhir:where(concept='...').value / 10000"
    }
  },
  "readonly": true
},
{
  // Dropdown select
  "type": "obs",
  "questionOptions": {
    "rendering": "select",
    "concept": "...",
    "answerConceptSetUuid": "CONCEPT_SET_UUID"
  }
},
{
  // Checkbox - boolean value
  "type": "obs",
  "questionOptions": {
    "rendering": "checkbox",
    "concept": "..."
  }
}
```

---

## Form Validation

### Validators Array

Each question can have multiple validators:

```json
"validators": [
  {
    "type": "date",
    "allowFutureDates": false
  },
  {
    "type": "required"
  },
  {
    "type": "minDate",
    "value": "2020-01-01"
  },
  {
    "type": "maxDate", 
    "value": "2026-12-31"
  },
  {
    "type": "pattern",
    "pattern": "^[0-9]{10}$"  // E.g., 10-digit number
  }
]
```

### Validator Types

| Type | Purpose | Example |
|------|---------|---------|
| `date` | Validates date format | `{ "type": "date", "allowFutureDates": false }` |
| `required` | Field mandatory | `{ "type": "required" }` |
| `minDate` | Minimum date allowed | `{ "type": "minDate", "value": "2020-01-01" }` |
| `maxDate` | Maximum date allowed | `{ "type": "maxDate", "value": "2026-12-31" }` |
| `pattern` | Regex validation | `{ "type": "pattern", "pattern": "^[0-9]+$" }` |
| `min` | Minimum value | `{ "type": "min", "value": 0 }` |
| `max` | Maximum value | `{ "type": "max", "value": 1000 }` |

---

## Conditional Visibility (Hide/Show Logic)

### Hide Object

```json
{
  "hide": {
    "hideWhenExpression": "!includes(answersToQuestions, 'HIV_STATUS', 'Positive')"
  }
}
```

### Hide When Expression Examples

```javascript
// Hide if HIV status is not Positive
"!includes(answersToQuestions, 'HIV_STATUS', 'Positive')"

// Hide if gender is Female
"answersToQuestions['gender'] !== 'F'"

// Hide if CD4 count > 500
"answersToQuestions['cd4_count'] <= 500"

// Show only if age >= 18
"answersToQuestions['age'] < 18"
```

---

## Calculated Fields

### Calculate Expressions

```json
{
  "type": "control",
  "id": "bmi",
  "label": "BMI",
  "readonly": true,
  "questionOptions": {
    "rendering": "number",
    "calculate": {
      "calculateExpression": "weight / (height * height)"
    }
  }
}
```

### API-Based Calculations

```json
{
  "type": "control",
  "id": "latestWeight",
  "label": "Latest Weight",
  "readonly": true,
  "questionOptions": {
    "rendering": "number",
    "calculate": {
      "calculateExpression": "resolve(api.getLatestObs(patient.id, '5089AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')).then(obs => obs?.valueQuantity?.value ?? null)"
    }
  }
}
```

---

## Form Submission Data Structure

### When form is submitted, data looks like:

```json
{
  "visit": {
    "visitDate": "2026-10-07",
    "visitType": "INITIAL"
  },
  "patient": {
    "id": "patient-uuid",
    "firstName": "John",
    "lastName": "Doe"
  },
  "observations": [
    {
      "concept": "5089AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
      "value": 75.5,
      "obsDatetime": "2026-10-07"
    },
    {
      "concept": "5090AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
      "value": 180,
      "obsDatetime": "2026-10-07"
    }
  ],
  "diagnosis": [
    {
      "code": "I10",
      "display": "Essential (primary) hypertension"
    }
  ]
}
```

---

## Common OpenMRS Concept UUIDs

Used in Ampath forms for pharmacy data:

```javascript
{
  // Vital Signs
  "5089AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "Weight (kg)",
  "5090AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "Height (cm)",
  "5087AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "Blood Pressure",
  "5085AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "Temperature (°C)",
  
  // HIV/AIDS
  "5497AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "HIV Status",
  "5356AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "CD4 Count",
  "5424AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "Viral Load",
  
  // Pharmacy
  "1282AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "Medication/Drug",
  "1255AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "Dose",
  "1318AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "Dosing Frequency",
  "1193AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "Route of Administration",
  
  // Diagnosis
  "160144AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA": "Diagnosis"
}
```

---

## Example: Combined Pharmacy Order Form Structure

The "Combined Pharmacy Order Form.json" contains:

### Treatment Information Page
- Visit Date (encounterDatetime)
- Latest Weight (calculated from patient obs)
- Latest Height (calculated from patient obs)
- BMI (calculated from weight and height)

### Medication Section
- Drug name (select from drug list)
- Dosage (number)
- Frequency (select: daily, twice daily, etc.)
- Duration (number of days)
- Route (select: oral, injection, etc.)

### Clinical Assessment
- Indication (text/select)
- Contraindications (text)
- Drug Interactions (text)
- Special Instructions (text)

### Validation Rules
- All required fields must be filled
- Visit date cannot be in future
- Drug must be selected from approved list
- Dosage must be positive number
- Duration must be 1-365 days

---

## Integration with Python App

### Form Upload Process:

1. **Upload**: JSON form file sent to `/api/forms/upload`
2. **Validation**: Backend validates JSON structure
3. **Storage**: Form stored in database with UUID
4. **Retrieval**: Python app fetches form via `/api/forms`
5. **Parsing**: Python app parses JSON and creates UI elements
6. **Filling**: User fills form for each client
7. **Submission**: Form data sent to `/api/submissions`

### Python App Form Rendering:

```python
class FormEngine:
    def parse_form(self, form_json):
        # Parse JSON structure
        form = json.loads(form_json)
        
        # Extract pages
        pages = form.get('pages', [])
        
        for page in pages:
            sections = page.get('sections', [])
            for section in sections:
                questions = section.get('questions', [])
                for question in questions:
                    # Create UI widget for each question
                    widget = self.create_question_widget(question)
                    
    def create_question_widget(self, question):
        question_type = question.get('type')
        rendering = question.get('questionOptions', {}).get('rendering')
        
        if rendering == 'date':
            return QDateEdit()
        elif rendering == 'number':
            return QSpinBox()
        elif rendering == 'select':
            return QComboBox()
        # ... etc
```

---

## Resources & References

### Official Documentation:
- [OpenMRS O3 Documentation](https://wiki.openmrs.org/display/projects/OpenMRS+3.0)
- [Ampath Form Module](https://github.com/AMPATH/openmrs-module-ampath)
- [OpenMRS Concepts](https://reference.openmrs.org/concepts/)

### Form Examples:
- Pharmacy Order Form (Combined)
- Adverse Drug Reaction Form
- Patient Visit Form
- Lab Result Form

### Tools:
- OpenMRS Form Builder UI (in O3)
- Form validator tools
- Concept browser

---

## Best Practices

1. **Form Design:**
   - Keep forms short (1-2 pages max)
   - Group related questions in sections
   - Use conditional visibility to reduce clutter

2. **Validation:**
   - Validate at both client and server level
   - Use meaningful error messages
   - Prevent future dates for historical data

3. **Data Entry:**
   - Pre-populate calculated fields
   - Auto-load previous values where applicable
   - Provide help text for complex fields

4. **Mobile Optimization:**
   - Test on mobile devices
   - Minimize required scrolling
   - Use touch-friendly controls

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Form not loading | Invalid JSON | Validate JSON structure |
| Fields not visible | Hide expression true | Check conditional logic |
| Calculations not working | Wrong concept UUID | Verify concept mapping |
| Validation not triggering | Validator misconfigured | Check validator syntax |
| Date picker not working | Wrong rendering type | Use "date" rendering |

---

Last Updated: 2026-10-07
Version: 1.0
