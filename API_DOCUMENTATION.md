# Community Pharmacy System - API Documentation

## Overview

This is a comprehensive healthcare data management system consisting of three main components:

1. **Python Pharmacy Desktop App** - PyQt6-based desktop application for local pharmacy management
2. **React Backend Server** - Express.js central server for data synchronization
3. **OpenMRS Sync Module** - Bi-directional sync between OpenMRS and central server

---

## Table of Contents

1. [Authentication](#authentication)
2. [Base URLs](#base-urls)
3. [Clients API](#clients-api)
4. [Forms API](#forms-api)
5. [Form Submissions API](#form-submissions-api)
6. [Pharmacies API](#pharmacies-api)
7. [Facilities API](#facilities-api)
8. [Sync API](#sync-api)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## Authentication

All API endpoints (except login/signup) require authentication using JWT tokens.

### Login

**Endpoint:** `POST /api/auth/login`

**Description:** Authenticate user and receive JWT token

**Request Body:**
```json
{
  "username": "pharmacist1",
  "password": "secure_password",
  "role": "pharmacy_staff"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid",
    "username": "pharmacist1",
    "email": "pharmacist1@pharmacy.com",
    "role": "pharmacy_staff",
    "fullName": "John Doe"
  }
}
```

**Status Codes:** 
- `200` - Success
- `401` - Invalid credentials
- `400` - Missing fields

### Signup

**Endpoint:** `POST /api/auth/signup`

**Description:** Register new user account

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@pharmacy.com",
  "password": "secure_password",
  "full_name": "New User",
  "role": "pharmacy_staff",
  "pharmacy_id": "pharmacy-uuid"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "userId": "new-user-uuid"
}
```

### Verify Token

**Endpoint:** `POST /api/auth/verify`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Token valid",
  "user": {
    "userId": "user-uuid",
    "username": "pharmacist1",
    "role": "pharmacy_staff"
  }
}
```

---

## Base URLs

- **Central Server:** `http://localhost:3001/api`
- **Python Pharmacy App:** `http://localhost:5000/api`
- **OpenMRS Server:** `http://localhost:8080/openmrs/ws/rest/v1`

---

## Clients API

### Get All Clients

**Endpoint:** `GET /api/clients`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `pharmacyId` (string, optional) - Filter by pharmacy
- `facilityId` (string, optional) - Filter by facility
- `status` (string, optional) - Filter by status (Active, Inactive, Transferred)
- `page` (number, default: 1) - Page number
- `limit` (number, default: 20) - Records per page

**Response:**
```json
{
  "message": "Clients retrieved successfully",
  "data": [
    {
      "id": "client-uuid",
      "pepfarId": "KE-001-001-001",
      "fullName": "James Mwangi",
      "phone": "0712345678",
      "dob": "1990-05-15",
      "gender": "M",
      "facility": "Central Hospital",
      "pharmacy_id": "pharmacy-uuid",
      "status": "Active",
      "assignedAt": "2024-01-15T10:30:00Z",
      "createdAt": "2024-01-01T08:00:00Z",
      "updatedAt": "2024-01-20T14:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

### Get Client by ID

**Endpoint:** `GET /api/clients/:clientId`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Client retrieved successfully",
  "data": {
    "id": "client-uuid",
    "pepfarId": "KE-001-001-001",
    "fullName": "James Mwangi",
    "phone": "0712345678",
    "email": "james@email.com",
    "dob": "1990-05-15",
    "gender": "M",
    "address": "123 Main Street",
    "city": "Nairobi",
    "district": "Westlands",
    "country": "Kenya",
    "facility": "Central Hospital",
    "pharmacy_id": "pharmacy-uuid",
    "hivStatus": "Positive",
    "cd4Count": "450",
    "viralLoad": "Undetectable",
    "currentARVs": ["Efavirenz", "Lamivudine", "Tenofovir"],
    "allergies": "Penicillin",
    "chronicConditions": ["Hypertension"],
    "status": "Active",
    "lastSync": "2024-01-20T14:30:00Z",
    "createdAt": "2024-01-01T08:00:00Z",
    "updatedAt": "2024-01-20T14:30:00Z"
  }
}
```

### Search Client by PEPFARID

**Endpoint:** `GET /api/clients/search/pepfarid/:pepfarId`

**Headers:** `Authorization: Bearer <token>`

**Response:**
Same as Get Client by ID

### Create/Upload Client

**Endpoint:** `POST /api/clients`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "pepfarId": "KE-001-001-002",
  "fullName": "Mary Kipchoge",
  "phone": "0723456789",
  "email": "mary@email.com",
  "dob": "1992-08-20",
  "gender": "F",
  "address": "456 Oak Avenue",
  "city": "Mombasa",
  "district": "Mombasa",
  "country": "Kenya",
  "facility": "Coast Hospital",
  "hivStatus": "Positive",
  "cd4Count": "550",
  "viralLoad": "Undetectable"
}
```

**Response:**
```json
{
  "message": "Client created/updated successfully",
  "data": {
    "id": "new-client-uuid",
    "pepfarId": "KE-001-001-002",
    "fullName": "Mary Kipchoge",
    "createdAt": "2024-01-21T09:00:00Z"
  }
}
```

### Bulk Upload Clients

**Endpoint:** `POST /api/clients/bulk/upload`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "clients": [
    {
      "pepfarId": "KE-001-001-003",
      "fullName": "Client 3",
      "phone": "0734567890",
      "facility": "Facility 1"
    },
    {
      "pepfarId": "KE-001-001-004",
      "fullName": "Client 4",
      "phone": "0745678901",
      "facility": "Facility 2"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Bulk upload completed",
  "results": [
    {
      "pepfarId": "KE-001-001-003",
      "status": "success",
      "clientId": "client-uuid-3"
    },
    {
      "pepfarId": "KE-001-001-004",
      "status": "success",
      "clientId": "client-uuid-4"
    }
  ]
}
```

### Assign Client to Pharmacy

**Endpoint:** `POST /api/clients/:clientId/assign-pharmacy`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "pharmacyId": "pharmacy-uuid"
}
```

**Response:**
```json
{
  "message": "Client assigned to pharmacy successfully",
  "data": {
    "id": "client-uuid",
    "pepfarId": "KE-001-001-001",
    "pharmacy_id": "pharmacy-uuid",
    "assigned_at": "2024-01-21T10:00:00Z"
  }
}
```

### Update Client

**Endpoint:** `PUT /api/clients/:clientId`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "phone": "0799999999",
  "hivStatus": "Positive",
  "cd4Count": "500"
}
```

**Response:**
```json
{
  "message": "Client updated successfully",
  "data": { ... }
}
```

### Delete Client

**Endpoint:** `DELETE /api/clients/:clientId`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Client deleted successfully"
}
```

---

## Forms API

### Get All Forms

**Endpoint:** `GET /api/forms`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 20)
- `active` (boolean, default: true)

**Response:**
```json
{
  "message": "Forms retrieved successfully",
  "data": [
    {
      "id": "form-uuid",
      "form_code": "FORM-001",
      "form_name": "ARV Refill Form",
      "description": "Form for ARV refill prescription",
      "version": 2,
      "created_by": "admin-uuid",
      "is_active": true,
      "createdAt": "2024-01-10T08:00:00Z",
      "updatedAt": "2024-01-20T15:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "pages": 1
}
```

### Get Form by ID

**Endpoint:** `GET /api/forms/:formId`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Form retrieved successfully",
  "data": {
    "id": "form-uuid",
    "form_code": "FORM-001",
    "form_name": "ARV Refill Form",
    "description": "Form for ARV refill prescription",
    "form_schema": {
      "id": "FORM-001",
      "name": "ARV Refill Form",
      "description": "Form for ARV refill prescription",
      "sections": [
        {
          "id": "section-1",
          "name": "Patient Information",
          "questions": [
            {
              "id": "client_id",
              "label": "Client ID",
              "type": "text",
              "required": true
            }
          ]
        }
      ]
    },
    "version": 2,
    "created_by": "admin-uuid",
    "is_active": true,
    "createdAt": "2024-01-10T08:00:00Z"
  }
}
```

### Upload New Form

**Endpoint:** `POST /api/forms/upload`

**Headers:** `Authorization: Bearer <token>` (Admin only)

**Request Body:**
```json
{
  "id": "FORM-002",
  "name": "Client Dispensing Form",
  "description": "Form for recording drug dispensing",
  "sections": [
    {
      "id": "section-1",
      "name": "Dispensing Details",
      "questions": [
        {
          "id": "drug_name",
          "label": "Drug Name",
          "type": "select",
          "required": true,
          "options": [
            { "label": "Efavirenz", "value": "efavirenz" },
            { "label": "Tenofovir", "value": "tenofovir" }
          ]
        },
        {
          "id": "quantity",
          "label": "Quantity Dispensed",
          "type": "number",
          "required": true,
          "min": 1,
          "max": 1000
        },
        {
          "id": "expiry_date",
          "label": "Expiry Date",
          "type": "date",
          "required": true
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "message": "Form created successfully",
  "data": {
    "id": "form-uuid",
    "form_code": "FORM-002",
    "form_name": "Client Dispensing Form",
    "version": 1,
    "is_active": true,
    "createdAt": "2024-01-21T10:00:00Z"
  }
}
```

### Update Form

**Endpoint:** `PUT /api/forms/:formId`

**Headers:** `Authorization: Bearer <token>` (Admin only)

**Request Body:** Same as Upload New Form

**Response:**
```json
{
  "message": "Form updated successfully",
  "data": {
    "id": "form-uuid",
    "form_name": "Client Dispensing Form",
    "version": 2,
    "updatedAt": "2024-01-21T11:00:00Z"
  }
}
```

### Deactivate Form

**Endpoint:** `PATCH /api/forms/:formId/deactivate`

**Headers:** `Authorization: Bearer <token>` (Admin only)

**Response:**
```json
{
  "message": "Form deactivated successfully",
  "data": {
    "id": "form-uuid",
    "is_active": false
  }
}
```

### Delete Form

**Endpoint:** `DELETE /api/forms/:formId`

**Headers:** `Authorization: Bearer <token>` (Admin only)

**Response:**
```json
{
  "message": "Form deleted successfully"
}
```

---

## Form Submissions API

### Submit Form

**Endpoint:** `POST /api/submissions/submit`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "formId": "form-uuid",
  "clientId": "client-uuid",
  "pepfarId": "KE-001-001-001",
  "timestamp": "2024-01-21T12:00:00Z",
  "fields": {
    "drug_name": "efavirenz",
    "quantity": 30,
    "expiry_date": "2025-06-15",
    "notes": "Patient counselled on adherence"
  }
}
```

**Response:**
```json
{
  "message": "Form submitted successfully",
  "submissionId": "submission-uuid",
  "data": {
    "id": "submission-uuid",
    "form_id": "form-uuid",
    "client_id": "client-uuid",
    "status": "submitted",
    "submitted_at": "2024-01-21T12:00:00Z"
  }
}
```

### Save Form as Draft

**Endpoint:** `POST /api/submissions/save-draft`

**Headers:** `Authorization: Bearer <token>`

**Request Body:** Same as Submit Form

**Response:**
```json
{
  "message": "Form saved as draft",
  "submissionId": "submission-uuid",
  "data": {
    "id": "submission-uuid",
    "status": "draft"
  }
}
```

### Get Submission by ID

**Endpoint:** `GET /api/submissions/:submissionId`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Submission retrieved successfully",
  "data": {
    "id": "submission-uuid",
    "form_id": "form-uuid",
    "client_id": "client-uuid",
    "submission_data": {
      "drug_name": "efavirenz",
      "quantity": 30
    },
    "status": "submitted",
    "submitted_at": "2024-01-21T12:00:00Z"
  }
}
```

### Get Client Submissions

**Endpoint:** `GET /api/submissions/client/:clientId/submissions`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 20)
- `status` (string, optional) - Filter by status

**Response:**
```json
{
  "message": "Client submissions retrieved",
  "data": [
    {
      "id": "submission-uuid-1",
      "form_id": "form-uuid",
      "form": { "form_name": "ARV Refill Form" },
      "status": "submitted",
      "submitted_at": "2024-01-21T12:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "pages": 1
}
```

### Update Submission Status

**Endpoint:** `PATCH /api/submissions/:submissionId/status`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "approved",
  "notes": "Approved by supervisor"
}
```

**Response:**
```json
{
  "message": "Submission status updated",
  "data": {
    "id": "submission-uuid",
    "status": "approved",
    "status_updated_at": "2024-01-21T13:00:00Z"
  }
}
```

### Delete Submission

**Endpoint:** `DELETE /api/submissions/:submissionId`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Submission deleted successfully"
}
```

---

## Pharmacies API

### Get All Pharmacies

**Endpoint:** `GET /api/pharmacies`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Pharmacies retrieved successfully",
  "data": [
    {
      "id": "pharmacy-uuid",
      "pharmacy_code": "PHARM-001",
      "pharmacy_name": "Central Pharmacy",
      "description": "Main pharmacy location",
      "address": "123 Health Street",
      "phone": "0712000000",
      "email": "pharmacy@health.com",
      "is_active": true,
      "createdAt": "2024-01-01T08:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

### Get Pharmacy by ID

**Endpoint:** `GET /api/pharmacies/:pharmacyId`

**Headers:** `Authorization: Bearer <token>`

**Response:** Same as single pharmacy object from Get All Pharmacies

### Create Pharmacy

**Endpoint:** `POST /api/pharmacies`

**Headers:** `Authorization: Bearer <token>` (Admin only)

**Request Body:**
```json
{
  "pharmacyCode": "PHARM-002",
  "pharmacyName": "Branch Pharmacy",
  "description": "Secondary location",
  "address": "456 Clinic Road",
  "phone": "0712000001",
  "email": "branch@health.com"
}
```

**Response:**
```json
{
  "message": "Pharmacy created successfully",
  "data": {
    "id": "pharmacy-uuid",
    "pharmacy_code": "PHARM-002",
    "pharmacy_name": "Branch Pharmacy",
    "api_key": "generated-api-key-string"
  }
}
```

### Regenerate API Key

**Endpoint:** `POST /api/pharmacies/:pharmacyId/regenerate-api-key`

**Headers:** `Authorization: Bearer <token>` (Admin only)

**Response:**
```json
{
  "message": "API key regenerated successfully",
  "api_key": "new-api-key-string"
}
```

### Get Pharmacy Statistics

**Endpoint:** `GET /api/pharmacies/:pharmacyId/stats`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Pharmacy statistics retrieved",
  "data": {
    "pharmacyId": "pharmacy-uuid",
    "pharmacyName": "Central Pharmacy",
    "clientsCount": 150,
    "submissionsCount": 1250,
    "lastSync": "2024-01-21T14:00:00Z"
  }
}
```

---

## Facilities API

### Get All Facilities

**Endpoint:** `GET /api/facilities`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Facilities retrieved successfully",
  "data": [
    {
      "id": "facility-uuid",
      "facility_code": "FAC-001",
      "facility_name": "Central Hospital",
      "description": "Main teaching hospital",
      "address": "123 Hospital Road",
      "phone": "0711000000",
      "email": "central@hospital.com",
      "district": "Nairobi",
      "is_active": true,
      "createdAt": "2024-01-01T08:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "pages": 1
}
```

### Assign Clients to Pharmacy

**Endpoint:** `POST /api/facilities/:facilityId/assign-clients-to-pharmacy`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "clientIds": ["client-uuid-1", "client-uuid-2", "client-uuid-3"],
  "pharmacyId": "pharmacy-uuid"
}
```

**Response:**
```json
{
  "message": "Clients assigned to pharmacy successfully",
  "assigned": 3
}
```

### Get Facility Clients

**Endpoint:** `GET /api/facilities/:facilityId/clients`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 50)

**Response:**
```json
{
  "message": "Facility clients retrieved",
  "data": [ ... ],
  "total": 500,
  "page": 1,
  "pages": 10
}
```

---

## Sync API

### Get Sync Logs

**Endpoint:** `GET /api/sync/logs`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page` (number, default: 1)
- `limit` (number, default: 50)
- `type` (string, optional)
- `status` (string, optional)

**Response:**
```json
{
  "message": "Sync logs retrieved",
  "data": [
    {
      "id": "log-uuid",
      "pharmacy_id": "pharmacy-uuid",
      "sync_type": "pharmacy_pull",
      "sync_status": "success",
      "records_count": 50,
      "createdAt": "2024-01-21T14:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 2
}
```

### Get Sync Status

**Endpoint:** `GET /api/sync/status`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Sync status retrieved",
  "data": {
    "lastSync": "2024-01-21T14:00:00Z",
    "lastSyncStatus": "success",
    "pendingSubmissions": 25,
    "systemHealthy": true
  }
}
```

### Pharmacy Pull Clients

**Endpoint:** `POST /api/sync/pharmacy/pull-clients`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "pharmacyId": "pharmacy-uuid"
}
```

**Response:**
```json
{
  "message": "Clients synced successfully",
  "data": [ ... ],
  "count": 150,
  "timestamp": "2024-01-21T14:30:00Z"
}
```

### Pharmacy Push Forms

**Endpoint:** `POST /api/sync/pharmacy/push-forms`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "pharmacyId": "pharmacy-uuid"
}
```

**Response:**
```json
{
  "message": "Forms synced successfully",
  "data": [ ... ],
  "count": 15,
  "timestamp": "2024-01-21T14:35:00Z"
}
```

### OpenMRS Pull Submissions

**Endpoint:** `POST /api/sync/openmrs/pull-submissions`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Submissions ready for OpenMRS",
  "data": [
    {
      "submissionId": "submission-uuid",
      "clientId": "client-uuid",
      "pepfarId": "KE-001-001-001",
      "formCode": "FORM-001",
      "submissionData": { ... },
      "submittedAt": "2024-01-21T12:00:00Z"
    }
  ],
  "count": 25,
  "timestamp": "2024-01-21T14:40:00Z"
}
```

### OpenMRS Confirm Sync

**Endpoint:** `POST /api/sync/openmrs/confirm-sync`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "submissions": [
    {
      "submissionId": "submission-uuid",
      "encounterId": "encounter-uuid-from-openmrs"
    }
  ]
}
```

**Response:**
```json
{
  "message": "Sync confirmation received",
  "syncedCount": 25,
  "timestamp": "2024-01-21T14:45:00Z"
}
```

---

## Error Handling

All errors return a JSON response with the following format:

```json
{
  "message": "Error description",
  "error": "Error details (optional)"
}
```

### Error Status Codes

- `400` - Bad Request (missing/invalid parameters)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `409` - Conflict (duplicate record)
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## Rate Limiting

Rate limiting is applied to all endpoints:

- **Limit:** 100 requests per 15 minutes per IP
- **Headers:** Rate limit info included in response headers
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets

**Response when rate limited (429):**
```json
{
  "message": "Too many requests, please try again later"
}
```

---

## Data Models

### Client
```json
{
  "id": "UUID",
  "pepfarId": "String (unique)",
  "fullName": "String",
  "phone": "String",
  "email": "String",
  "dob": "Date",
  "gender": "String (M/F)",
  "address": "String",
  "city": "String",
  "district": "String",
  "country": "String",
  "facility_id": "UUID",
  "pharmacy_id": "UUID",
  "hivStatus": "String",
  "cd4Count": "String",
  "viralLoad": "String",
  "currentARVs": "Array",
  "allergies": "String",
  "chronicConditions": "Array",
  "status": "String (Active/Inactive/Transferred)",
  "lastSync": "DateTime",
  "createdAt": "DateTime",
  "updatedAt": "DateTime"
}
```

### Form
```json
{
  "id": "UUID",
  "form_code": "String (unique)",
  "form_name": "String",
  "description": "String",
  "form_schema": "JSON",
  "version": "Integer",
  "created_by": "UUID",
  "is_active": "Boolean",
  "createdAt": "DateTime",
  "updatedAt": "DateTime"
}
```

### FormSubmission
```json
{
  "id": "UUID",
  "form_id": "UUID",
  "client_id": "UUID",
  "pharmacy_id": "UUID",
  "submitted_by": "UUID",
  "submission_data": "JSON",
  "status": "String (draft/submitted/approved/rejected/synced)",
  "submitted_at": "DateTime",
  "synced_at": "DateTime",
  "openmrs_encounter_id": "String",
  "createdAt": "DateTime",
  "updatedAt": "DateTime"
}
```

---

## Setup Instructions

### Prerequisites
- Node.js 14+
- Python 3.8+
- PostgreSQL 12+
- OpenMRS 2.x

### React Backend Setup

```bash
cd react-backend-server
npm install
cp .env.example .env
# Update .env with your configuration
npm run migrate
npm start
```

### Python App Setup

```bash
cd python-pharmacy-app
pip install -r requirements.txt
python main.py
```

### OpenMRS Sync Setup

```bash
cd OpenMRS-Sync-Module
npm install
cp .env.example .env
# Update .env with your OpenMRS credentials
npm start
```

---

## Contact & Support

For issues, questions, or contributions, please contact:
- **Email:** support@pharmacy.com
- **Documentation:** https://docs.pharmacy.com
- **Issue Tracker:** https://github.com/pharmacy-sync/issues
