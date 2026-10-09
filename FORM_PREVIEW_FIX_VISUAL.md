# Form Preview Fix - Visual Guide

## Problem: Raw JSON Display
When a user clicked "Preview Form" on a raw JSON form (not in OpenMRS structured format), they saw:

```
{
  "test_field": "test_value",
  "timestamp": 1791547022.1651568
}
```

❌ **WRONG**: Shows raw JSON text instead of interactive form fields

---

## Solution: Interactive Input Fields

### Before Fix
```
┌─────────────────────────────────────────┐
│ Preview Form: My Form                   │
├─────────────────────────────────────────┤
│                                         │
│ {                                       │
│   "test_field": "test_value",          │
│   "timestamp": 1791547022.1651568      │
│ }                                       │
│                                         │
└─────────────────────────────────────────┘
```

### After Fix
```
┌─────────────────────────────────────────┐
│ Preview Form: My Form                   │
├─────────────────────────────────────────┤
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ Test Field                          │ │
│ ├─────────────────────────────────────┤ │
│ │ [test_value                        ]│ │
│ └─────────────────────────────────────┘ │
│                                         │
│ (timestamp field hidden - internal)    │
│                                         │
└─────────────────────────────────────────┘
```

✅ **CORRECT**: Shows interactive input fields with readable labels

---

## Implementation Flow

### Step 1: Check Form Data Structure
```
                   ┌──────────────────┐
                   │  render_form_    │
                   │  preview()       │
                   └─────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Has pages?      │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                   YES               NO
                    │                 │
            Render  │          ┌──────▼──────┐
            pages & │          │ Has         │
            sections│          │ sections?   │
                    │          └──────┬──────┘
                    │                 │
                    │        ┌────────┴────────┐
                    │        │                 │
                    │       YES               NO
                    │        │                 │
                    │   Render       ┌─────────▼──────────┐
                    │   sections     │ render_raw_form_   │
                    │        │       │ data() ← NEW       │
                    └────────┼───────┘                    │
                             │                           │
                             └──────────────┬────────────┘
                                           │
                                  ┌────────▼─────────┐
                                  │ Render fields as │
                                  │ interactive UI   │
                                  └──────────────────┘
```

### Step 2: Process Raw Form Data
```
For each key-value pair in form_data:

┌─────────────────────────────────────────┐
│ 1. Check if internal field              │
│    (timestamp, id, uuid, _-prefixed)    │
│    └─> Skip if yes                      │
├─────────────────────────────────────────┤
│ 2. Format field label                   │
│    test_field → "Test Field"            │
│    myAttribute → "My Attribute"         │
├─────────────────────────────────────────┤
│ 3. Determine value type                 │
│    bool → Checkbox                      │
│    int/float → SpinBox                  │
│    list/dict → TextEdit (JSON)          │
│    string → LineEdit                    │
├─────────────────────────────────────────┤
│ 4. Create disabled/read-only widget     │
│    └─> Add to layout                    │
└─────────────────────────────────────────┘
```

### Step 3: Create Type-Specific Widgets

```python
Value Type          Widget Type         Display Format
─────────────────────────────────────────────────────────
bool (True/False)   QCheckBox           ☑ Checked or ☐ Unchecked
                    (disabled)

int (42)            QSpinBox            [        42        ]
float (3.14)        QDoubleSpinBox      [       3.14       ]
                    (disabled)

string ("hello")    QLineEdit           [ hello            ]
                    (read-only)

list ([1,2,3])      QTextEdit           [                  ]
dict ({a:b})        (JSON formatted)    [ [                 ]
                    (read-only)         [   1,             ]
                                        [   2,             ]
                                        [   3              ]
                                        [ ]                ]
```

---

## Code Structure

### New Methods Added to FormPreviewDialog

```
FormPreviewDialog
│
├── render_form_preview()        [EXISTING - UPDATED]
│   └── Added fallback call to render_raw_form_data()
│
├── render_raw_form_data()       [NEW]
│   ├── Validates data is dict
│   ├── Iterates through key-value pairs
│   ├── Skips internal fields
│   ├── Formats labels
│   └── Creates widgets for each field
│
├── _format_field_label()        [NEW - HELPER]
│   ├── Converts snake_case → Title Case
│   └── Converts camelCase → Title Case
│
└── _create_input_widget()       [NEW - HELPER]
    ├── Handles bool → QCheckBox
    ├── Handles int → QSpinBox
    ├── Handles float → QDoubleSpinBox
    ├── Handles list/dict → QTextEdit
    └── Handles string → QLineEdit
```

---

## Example: Test Form Data

### Input
```python
form_data = {
    "test_field": "test_value",
    "timestamp": 1791547022.1651568,  # Internal - hidden
    "count": 42,
    "active": True,
    "score": 3.14,
    "tags": ["important", "urgent"],
    "metadata": {"version": "1.0"}
}
```

### Processing
```
✓ test_field → "Test Field" + LineEdit("test_value")
✗ timestamp → SKIPPED (internal field)
✓ count → "Count" + QSpinBox(42)
✓ active → "Active" + QCheckBox(checked)
✓ score → "Score" + QDoubleSpinBox(3.14)
✓ tags → "Tags" + QTextEdit(["important", "urgent"])
✓ metadata → "Metadata" + QTextEdit({"version": "1.0"})
```

### Output UI
```
┌──────────────────────────────────────────┐
│ Preview Form: Test Form                  │
├──────────────────────────────────────────┤
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Test Field                           │ │
│ ├──────────────────────────────────────┤ │
│ │ [test_value                         ]│ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Count                                │ │
│ ├──────────────────────────────────────┤ │
│ │ [            42            ]         │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Active                               │ │
│ ├──────────────────────────────────────┤ │
│ │ ☑ (checked)                         │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Score                                │ │
│ ├──────────────────────────────────────┤ │
│ │ [           3.14           ]         │ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Tags                                 │ │
│ ├──────────────────────────────────────┤ │
│ │ [                                   ]│ │
│ │ [                                   ]│ │
│ │ ["important", "urgent"]             │ │
│ │ [                                   ]│ │
│ └──────────────────────────────────────┘ │
│                                          │
│ ┌──────────────────────────────────────┐ │
│ │ Metadata                             │ │
│ ├──────────────────────────────────────┤ │
│ │ [                                   ]│ │
│ │ [                                   ]│ │
│ │ {                                   │ │
│ │   "version": "1.0"                  │ │
│ │ }                                   │ │
│ │ [                                   ]│ │
│ └──────────────────────────────────────┘ │
│                                          │
└──────────────────────────────────────────┘
```

---

## Key Features

### ✅ Type-Aware Rendering
- Different widgets for different data types
- Appropriate display format for each type
- Disabled/read-only for preview mode

### ✅ Readable Labels
- Converts `test_field` → "Test Field"
- Converts `myAttribute` → "My Attribute"
- Handles both snake_case and camelCase

### ✅ Internal Fields Hidden
- Skips: timestamp, id, uuid, _id, form_id, version
- Skips: Any field starting with underscore (_)
- Shows only user-facing fields

### ✅ JSON Formatting
- Complex structures (list, dict) shown with proper indentation
- JSON format makes nested data readable
- Read-only for preview

### ✅ Graceful Fallback
- Works with any form data format
- No crashes on unexpected data
- Shows appropriate message if no fields found

---

## Error Handling

```python
# If form_data is not a dict
if not isinstance(self.form_data, dict):
    → Display as text in QTextEdit
    → Read-only mode

# If form_data is empty or no displayable fields
if fields_rendered == 0:
    → Show message: "No form fields to display"
    → Styled with italic/gray text

# If field value cannot be converted to string
else clause handles string conversion:
    → str(value) ensures no exceptions
```

---

## Testing Scenarios

### Scenario 1: Raw JSON Form
```python
form_data = {"test_field": "test_value", "timestamp": 1791547022.1651568}
Result: ✅ Shows "Test Field" with LineEdit, hides timestamp
```

### Scenario 2: Structured Form (OpenMRS)
```python
form_data = {
    "pages": [{
        "sections": [{
            "questions": [...]
        }]
    }]
}
Result: ✅ Uses existing render_section() and render_question()
```

### Scenario 3: Mixed Format Form
```python
form_data = {
    "sections": [{...}],
    "metadata": {...}
}
Result: ✅ Uses render_section() for sections, skips metadata
```

### Scenario 4: Empty Form
```python
form_data = {} or None
Result: ✅ Shows "No form fields to display" message
```

---

## Commit Details

**Commit**: `af394a1`
**Date**: 2026-10-09
**Author**: Copilot
**Changes**:
- Removed 933 lines of duplicate code
- Added 200+ lines of new form rendering logic
- Completely resolves form preview raw JSON display issue

---

## Summary

The form preview fix transforms the display from raw JSON text to interactive, type-aware input fields that are properly labeled and formatted. This provides a much better user experience when previewing forms with unstructured data.
