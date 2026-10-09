# Forms Management System - Quick Start Guide

## For Administrators (React App)

### Creating a New Form

1. **Navigate to Forms Management**
   - Click "Forms" in the sidebar/navigation
   - You'll see the Forms Management page with a list of existing forms

2. **Upload a Form**
   - Click "+ Upload New Form" button
   - Choose upload method:
     - **File Upload**: Select a JSON file from your computer
     - **Text Editor**: Paste JSON directly into the editor
   - Click "Upload" or "Save"
   - Form appears in your forms list

3. **Form JSON Structure**
```json
{
  "name": "My Form Title",
  "description": "Form description",
  "category": "medical",
  "sections": [
    {
      "name": "Section 1",
      "questions": [
        {
          "id": "q_1",
          "label": "Question Text",
          "type": "text",
          "required": true,
          "placeholder": "Enter answer..."
        }
      ]
    }
  ]
}
```

### Editing an Existing Form

1. Find the form in the grid
2. Click "✏️ Edit" button
3. Modify the form structure:
   - Edit form name/description
   - Add/remove sections
   - Add/remove/edit questions
4. Click "Save" to persist changes
5. Form version is automatically incremented

### Previewing a Form

1. Find the form in the grid
2. Click "👁️ Preview" button
3. Test the form:
   - Fill in all fields
   - Toggle between "Form View" and "JSON View"
   - Click "Submit" to test submission
4. Click back arrow to return to forms list

### Managing Forms

| Action | Button | What Happens |
|--------|--------|--------------|
| Download | ⬇️ Download | Download form as JSON file |
| Deactivate | 🚫 Deactivate | Mark form as inactive (hidden from clients) |
| Delete | 🗑️ Delete | Permanently delete form |

### Searching Forms

1. Use the search bar at the top
2. Search by form name or description
3. Results filter in real-time

---

## For Pharmacy Clients (Python Desktop App)

### Downloading Forms from Server

1. **Open Python App**
   - Launch the pharmacy management application

2. **Navigate to Forms Management**
   - Click "Forms Management" in the menu
   - Go to "Available Forms" tab

3. **Download Forms**
   - Click blue "Download Forms from Server" button
   - Wait for download to complete
   - Success message appears
   - Forms now available in your local list

### Filling Out a Form

1. **Select a Form**
   - Browse available forms in the list
   - Click on a form to select it

2. **Preview & Fill**
   - Form opens in preview mode
   - All input fields are interactive
   - Fill in all required fields (marked with *)
   - Optional fields can be left blank

3. **Submit Form**
   - After filling all required fields
   - Click "Submit" button
   - Form response is sent to server
   - Confirmation message appears

### Form Input Types

You may encounter these input types:

| Type | What to Do |
|------|-----------|
| **Text** | Type in any text |
| **Number** | Enter numeric values only |
| **Email** | Enter valid email address |
| **Date** | Click to select from date picker |
| **Textarea** | Type in multi-line text area |
| **Dropdown** | Click to select from options |
| **Checkbox** | Check boxes for applicable options |
| **Radio Button** | Select one option from group |

---

## API Quick Reference

### For Backend Integration

#### Download Forms (Python App)
```
GET /api/forms
Authorization: Bearer <jwt_token>

Response:
{
  "success": true,
  "data": [
    {
      "id": "form_123",
      "form_name": "Form Title",
      "form_data": { /* form structure */ },
      "version": 1,
      "is_active": true
    }
  ]
}
```

#### Submit Form Response (Python App)
```
POST /api/form-submissions
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "form_id": "form_123",
  "client_id": "client_456",
  "form_response": {
    "q_1": "answer_value",
    "q_2": "another_answer"
  }
}

Response:
{
  "success": true,
  "submission_id": "sub_789"
}
```

#### Upload Form (React Admin)
```
POST /api/forms/upload
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "form_name": "My Form",
  "description": "...",
  "form_data": { /* form structure */ }
}

Response:
{
  "success": true,
  "form": {
    "id": "form_new_id",
    "form_uuid": "uuid-string"
  }
}
```

---

## Question Types Reference

### Text
- Single line text input
- Good for: Names, emails, short answers
- Example: "What is your name?"

### Textarea
- Multi-line text input
- Good for: Descriptions, comments, long answers
- Example: "Describe your symptoms"

### Number
- Numeric input only
- Good for: Age, quantity, measurements
- Example: "How many tablets?"

### Email
- Email validation included
- Good for: Contact information
- Example: "Enter your email"

### Date
- Date picker calendar
- Good for: Birth dates, appointment dates
- Example: "Date of visit?"

### Select (Dropdown)
- Choose one from predefined options
- Good for: Categories, status, yes/no
- Example: "Select gender: Male/Female/Other"

### Checkbox
- Check multiple options
- Good for: Multiple selections
- Example: "Select all symptoms that apply"

### Radio Button
- Select exactly one option
- Good for: Single choice from group
- Example: "Severity: Low/Medium/High"

---

## Troubleshooting

### Form Won't Upload
**Problem**: Upload fails with error message
- **Solution**: 
  - Check JSON syntax is valid
  - Ensure form has at least one section
  - Form name is required
  - Try uploading smaller form first

### Forms Not Downloading
**Problem**: Download button doesn't work in Python app
- **Solution**:
  - Check internet connection
  - Verify you're logged in
  - Check if server is running
  - Look at console for error messages

### Form Fields Won't Save Answers
**Problem**: Data entered into form disappears
- **Solution**:
  - Check all required fields are filled (marked with *)
  - Try submitting again
  - Clear form and start over
  - Check internet connection

### Preview Shows Blank Form
**Problem**: No fields appear in form preview
- **Solution**:
  - Check form has questions in sections
  - Verify form JSON structure is correct
  - Try editing and re-saving form
  - Download form JSON to verify structure

### Column Visibility Menu Crashes
**Problem**: Right-click on column causes error
- **Solution**:
  - Update to latest Python app version
  - Issue was fixed in recent update
  - Clear app cache if problem persists

---

## Best Practices

### Creating Forms
- ✅ Use clear, descriptive question labels
- ✅ Make only essential fields required
- ✅ Use appropriate input types for data
- ✅ Add placeholder text for guidance
- ✅ Group related questions in sections
- ✅ Test form before distributing to clients

### Filling Forms
- ✅ Read instructions carefully
- ✅ Fill all fields marked with *
- ✅ Double-check answers before submitting
- ✅ Submit while internet is available
- ✅ Note form ID in case you need to reference it

### Managing Forms
- ✅ Version control: Save old forms before major changes
- ✅ Deactivate instead of delete when unsure
- ✅ Keep form names descriptive
- ✅ Add descriptions to explain form purpose
- ✅ Test form thoroughly before marking active

---

## Example: Creating a "Patient Registration" Form

### Step 1: Prepare JSON
```json
{
  "name": "Patient Registration",
  "description": "Initial patient information collection",
  "category": "medical",
  "sections": [
    {
      "name": "Personal Information",
      "questions": [
        {
          "id": "first_name",
          "label": "First Name",
          "type": "text",
          "required": true
        },
        {
          "id": "last_name",
          "label": "Last Name",
          "type": "text",
          "required": true
        },
        {
          "id": "dob",
          "label": "Date of Birth",
          "type": "date",
          "required": true
        },
        {
          "id": "gender",
          "label": "Gender",
          "type": "select",
          "required": true,
          "options": [
            {"value": "M", "label": "Male"},
            {"value": "F", "label": "Female"},
            {"value": "O", "label": "Other"}
          ]
        }
      ]
    },
    {
      "name": "Contact Information",
      "questions": [
        {
          "id": "email",
          "label": "Email Address",
          "type": "email",
          "required": false
        },
        {
          "id": "phone",
          "label": "Phone Number",
          "type": "text",
          "required": true
        }
      ]
    }
  ]
}
```

### Step 2: Upload Form
1. Go to Forms Management in React
2. Click "+ Upload New Form"
3. Paste JSON in text editor
4. Click "Upload"
5. See "Form uploaded successfully!" message

### Step 3: Test with Preview
1. Find form in grid
2. Click "👁️ Preview"
3. Fill in test data
4. Click "Submit"
5. Click back to return

### Step 4: Distribute to Clients
1. Forms available in Python app
2. Clients download from Python app
3. Clients see form in their available forms
4. Clients can preview and fill

---

## Common Errors & Solutions

| Error | Cause | Fix |
|-------|-------|-----|
| "Form must have name" | Missing form name | Add `"name": "..."` to JSON |
| "Invalid JSON" | JSON syntax error | Check brackets/quotes/commas |
| "Network error" | Server not accessible | Check server is running |
| "Unauthorized" | Invalid or expired token | Log in again |
| "Form not found" | Form ID is wrong | Verify form exists |

---

## Support Resources

- **Detailed Documentation**: See [FORMS_MANAGEMENT_COMPLETE_2026_10_09.md](./FORMS_MANAGEMENT_COMPLETE_2026_10_09.md)
- **Architecture Guide**: See [FORMS_SYSTEM_ARCHITECTURE.md](./FORMS_SYSTEM_ARCHITECTURE.md)
- **API Documentation**: See backend API docs in React server
- **Error Logs**: Check browser console (React) or Python console (App)

---

## Version Information

- **Forms System Version**: 1.0
- **Last Updated**: 2026-10-09
- **React App Version**: Check App.jsx
- **Python App Version**: Check main_window.py

---

## Quick Links

- React Forms Management: http://localhost:3000/ (navigate to Forms)
- Python App: Run main.py from python-pharmacy-app/
- API Server: http://localhost:3000/api
- API Docs: [FORMS_MANAGEMENT_COMPLETE_2026_10_09.md](./FORMS_MANAGEMENT_COMPLETE_2026_10_09.md)

---

**Last Updated**: 2026-10-09
**Status**: ✅ Ready for Production
