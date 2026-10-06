# System Architecture Documentation

## Overview

The Community Pharmacy System is a comprehensive healthcare data management platform designed for resource-limited settings. It enables seamless data flow between OpenMRS installations, health facilities, and community pharmacies.

## System Components

### 1. Python Pharmacy Desktop Application
- **Technology:** PyQt6, SQLite, Python 3.8+
- **Purpose:** Local pharmacy management and form handling
- **Key Features:**
  - Role-based access control (Admin, Pharmacy Staff, Facility Manager)
  - JSON form engine with conditional logic
  - Client data management
  - Offline-first architecture
  - Automatic sync with central server

### 2. React Backend Server
- **Technology:** Express.js, Node.js, PostgreSQL
- **Purpose:** Central data hub and synchronization engine
- **Key Features:**
  - RESTful API for all operations
  - User authentication and authorization
  - Data persistence and backup
  - Audit logging
  - Rate limiting and security

### 3. OpenMRS Sync Module
- **Technology:** Node.js, OpenMRS REST API
- **Purpose:** Bi-directional sync between OpenMRS and central server
- **Key Features:**
  - Automated form submission to OpenMRS
  - Patient data updates from OpenMRS
  - Encounter creation and management
  - Error handling and retry logic

---

## Data Flow

### 1. Client Creation Flow

```
Health Facility (OpenMRS)
    ↓
Facility Staff logs into Central Server
    ↓
Uploads/creates client records (PEPFARID, demographics)
    ↓
Central Server stores in PostgreSQL
    ↓
Pharmacy App requests sync
    ↓
Pharmacy downloads clients to SQLite
    ↓
Pharmacist can now view and manage client data
```

### 2. Form Management Flow

```
Admin logs into Central Server
    ↓
Uploads OpenMRS-style JSON form
    ↓
Central Server validates and stores form
    ↓
Form versioning managed (v1, v2, etc.)
    ↓
Pharmacy App requests available forms
    ↓
Downloads forms to local SQLite
    ↓
Pharmacist selects client and form
    ↓
Completes form with conditional logic
    ↓
Submits form to central server
```

### 3. Form Submission Flow

```
Pharmacist fills form for client
    ↓
Saves as draft or submits
    ↓
Pharmacy App sends to Central Server
    ↓
Central Server stores submission
    ↓
OpenMRS Sync Module periodically checks for submissions
    ↓
Creates OpenMRS encounter with form data
    ↓
Maps form fields to OpenMRS concepts
    ↓
Submission marked as synced
    ↓
OpenMRS has encounter with all data
```

### 4. Patient Update Flow

```
Patient seen at OpenMRS facility
    ↓
Encounter created with updated clinical data
    ↓
OpenMRS Sync Module pulls updates
    ↓
Sends updates to Central Server
    ↓
Central Server distributes to assigned pharmacy
    ↓
Pharmacy App refreshes client data
    ↓
Pharmacist sees updated patient information
```

---

## Database Schema

### Python Pharmacy App (SQLite)

```sql
-- Users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clients table
CREATE TABLE clients (
  id UUID PRIMARY KEY,
  pepfarid TEXT UNIQUE NOT NULL,
  full_name TEXT NOT NULL,
  dob DATE,
  gender TEXT,
  phone TEXT,
  email TEXT,
  address TEXT,
  city TEXT,
  district TEXT,
  country TEXT,
  facility_id TEXT,
  pharmacy_id TEXT,
  hiv_status TEXT,
  cd4_count TEXT,
  viral_load TEXT,
  current_arvs TEXT,
  allergies TEXT,
  chronic_conditions TEXT,
  status TEXT DEFAULT 'Active',
  last_sync TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forms table
CREATE TABLE forms (
  id UUID PRIMARY KEY,
  form_code TEXT UNIQUE NOT NULL,
  form_name TEXT NOT NULL,
  description TEXT,
  form_schema TEXT NOT NULL,
  version INTEGER DEFAULT 1,
  is_active BOOLEAN DEFAULT true,
  created_by TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Form submissions table
CREATE TABLE form_submissions (
  id UUID PRIMARY KEY,
  form_id TEXT NOT NULL,
  client_id TEXT NOT NULL,
  submission_data TEXT NOT NULL,
  status TEXT DEFAULT 'draft',
  submitted_by TEXT,
  submitted_at TIMESTAMP,
  synced_at TIMESTAMP,
  openmrs_encounter_id TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sync logs table
CREATE TABLE sync_logs (
  id UUID PRIMARY KEY,
  sync_type TEXT NOT NULL,
  sync_status TEXT NOT NULL,
  records_count INTEGER,
  sync_data TEXT,
  error_message TEXT,
  synced_by TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Central Server (PostgreSQL)

```sql
-- Similar schema as Python app but with additional fields for
-- audit trails, multiple facility/pharmacy support,
-- and advanced permission management

-- Additional tables:
CREATE TABLE pharmacies (
  id UUID PRIMARY KEY,
  pharmacy_code TEXT UNIQUE NOT NULL,
  pharmacy_name TEXT NOT NULL,
  description TEXT,
  address TEXT,
  phone TEXT,
  email TEXT,
  api_key TEXT UNIQUE NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE facilities (
  id UUID PRIMARY KEY,
  facility_code TEXT UNIQUE NOT NULL,
  facility_name TEXT NOT NULL,
  description TEXT,
  address TEXT,
  phone TEXT,
  email TEXT,
  district TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sync_logs (
  id UUID PRIMARY KEY,
  pharmacy_id TEXT,
  sync_type TEXT NOT NULL,
  sync_status TEXT NOT NULL,
  records_count INTEGER,
  sync_data TEXT,
  error_message TEXT,
  synced_by TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  user_id TEXT NOT NULL,
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id TEXT,
  old_value TEXT,
  new_value TEXT,
  ip_address TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Security Architecture

### Authentication & Authorization

1. **JWT Tokens**
   - Issued on login
   - 24-hour expiration
   - Refresh token mechanism
   - Revocation on logout

2. **Role-Based Access Control (RBAC)**
   - Admin: Full system access
   - Pharmacy Staff: Limited to assigned pharmacy
   - Facility Manager: Can create/manage clients
   - OpenMRS Sync: Scheduled sync access only

3. **API Key Authentication**
   - For pharmacy apps to central server
   - Regenerable per pharmacy
   - Rate limiting per key

### Data Security

1. **Data in Transit**
   - HTTPS/TLS encryption
   - Secure headers (Helmet.js)
   - CORS restrictions

2. **Data at Rest**
   - Database encryption (optional)
   - Sensitive fields hashed/encrypted
   - Backup encryption

3. **Audit Logging**
   - All data access logged
   - Change history maintained
   - IP address tracking
   - Compliance ready (HIPAA-like)

---

## Deployment Architecture

### Development Environment

```
Local Machine
├── Python App (localhost:5000)
├── React Backend (localhost:3001)
├── PostgreSQL (localhost:5432)
├── OpenMRS (localhost:8080)
└── OpenMRS Sync Module (localhost:3002)
```

### Production Environment

```
Production Server
├── API Server (Node.js)
│   ├── Express Application
│   ├── Load Balancer
│   └── Reverse Proxy (Nginx)
├── Database Server
│   └── PostgreSQL (replicated)
├── Cache Server
│   └── Redis
├── OpenMRS Server
│   └── Tomcat/Docker
├── Sync Module
│   └── Node.js Service
└── Backup & Storage
    └── S3/Cloud Storage
```

### Docker Composition

```dockerfile
# React Backend
docker-compose up -d postgres redis express-server openmrs-server sync-module

# Python App (local installation on pharmacies)
python main.py
```

---

## API Architecture

### REST Endpoints Organization

```
/api/auth
  POST /signup
  POST /login
  POST /verify
  POST /refresh
  POST /logout

/api/clients
  GET / - List all
  GET /:id - Get details
  POST / - Create
  PUT /:id - Update
  DELETE /:id - Delete
  POST /:id/assign-pharmacy
  POST /bulk/upload

/api/forms
  GET / - List forms
  GET /:id - Get form
  POST /upload - Create new
  PUT /:id - Update
  DELETE /:id - Deactivate
  GET /:id/submissions

/api/submissions
  POST /submit - Submit form
  POST /save-draft - Save draft
  GET /:id - Get submission
  PATCH /:id/status - Update status
  GET /client/:clientId/submissions

/api/pharmacies
  GET / - List
  GET /:id - Details
  POST / - Create (admin)
  POST /:id/regenerate-api-key
  GET /:id/stats

/api/facilities
  GET / - List
  POST /:id/assign-clients-to-pharmacy
  GET /:id/clients

/api/sync
  GET /logs
  GET /status
  POST /pharmacy/pull-clients
  POST /pharmacy/push-forms
  POST /openmrs/pull-submissions
  POST /openmrs/confirm-sync
```

---

## Sync Strategy

### Pharmacy to Central Server Sync

1. **Pull Operations (Pharmacy → Central)**
   - Client list (once, then updates)
   - Available forms (periodic)
   - Settings/configuration

2. **Push Operations (Pharmacy → Central)**
   - Form submissions
   - Sync acknowledgments
   - Error reports

3. **Sync Schedule**
   - Default: Every 5 minutes
   - Configurable per installation
   - Manual trigger available

### Central Server to OpenMRS Sync

1. **Pull Operations (Central → OpenMRS)**
   - Patient updates
   - Encounter history
   - Lab results

2. **Push Operations (Central → OpenMRS)**
   - Form submission as encounters
   - Observation data
   - Patient demographics updates

3. **Sync Schedule**
   - Default: Every 5 minutes
   - Prioritize failed items
   - Batch processing (100 per sync)

### Conflict Resolution

```
Scenario: Same patient updated in multiple locations
Resolution:
1. Timestamp-based (latest wins)
2. User-based priority
3. Manual review queue
4. Audit trail maintained
```

---

## Performance Optimization

### Database Optimization
- Indexed queries on PEPFARID, pharmacy_id, facility_id
- Connection pooling
- Query caching for forms
- Archived data partitioning

### API Optimization
- Response pagination (20-100 records)
- Gzip compression
- Caching headers
- Batch endpoints for bulk operations

### Sync Optimization
- Batch processing (100 records per sync)
- Partial sync capability
- Network resilience
- Retry with exponential backoff

---

## Disaster Recovery

### Backup Strategy
- Daily database backups
- 30-day retention
- Off-site storage
- Point-in-time recovery capability

### Failover Strategy
- Database replication (primary-backup)
- Load balancer failover
- Health checks (30s interval)
- Automatic failover <2 minutes

### Recovery Time Objectives (RTO)
- API Server: < 5 minutes
- Database: < 30 minutes
- Full system: < 1 hour

### Recovery Point Objectives (RPO)
- Transaction logs: continuous
- Database snapshots: daily
- Data loss: < 1 hour

---

## Monitoring & Alerting

### Key Metrics
- API response time (target: <200ms)
- Database query time (target: <100ms)
- Sync success rate (target: >99%)
- Form submission errors (target: <1%)
- System availability (target: 99.9%)

### Monitoring Tools
- Application Performance Monitoring (APM)
- Error tracking (Sentry/Rollbar)
- Log aggregation (ELK Stack)
- System monitoring (Prometheus/Grafana)

### Alerting Thresholds
- High error rate (>5%)
- Sync failures (>3 consecutive)
- Database connection pool exhaustion
- Disk space low (<20%)
- Memory usage high (>85%)

---

## Scalability Roadmap

### Phase 1: Single Region (Current)
- Single PostgreSQL server
- Single API server
- Basic sync module

### Phase 2: High Availability
- Database replication
- Load-balanced API servers
- Redis caching
- CDN for static assets

### Phase 3: Multi-Region
- Regional databases
- Data replication
- Regional sync coordinators
- Geo-distributed load balancing

### Phase 4: Global Scale
- Multiple independent regions
- Data federation
- Federated identity
- Global audit trail

---

## Compliance & Standards

### Healthcare Standards
- HL7/FHIR API compatibility
- OpenMRS module standards
- WHO data exchange formats

### Security Standards
- OWASP Top 10 compliance
- HIPAA-like requirements
- ISO 27001 practices
- Encryption standards (AES-256)

### Data Standards
- UTF-8 encoding
- ISO 8601 dates/times
- ISO 3166 country codes
- PEPFAR ID format compliance

---

## Maintenance & Operations

### Regular Maintenance Tasks
- Database optimization (weekly)
- Log rotation (daily)
- Security patches (immediately)
- Dependency updates (monthly)

### Documentation Updates
- API changes
- Schema migrations
- Known issues
- Performance tuning

### Support Procedures
- Issue prioritization
- Incident response
- Post-incident review
- Continuous improvement
