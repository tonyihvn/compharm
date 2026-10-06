# Community Pharmacy System

## 🏥 Professional Healthcare Data Management Platform

A comprehensive, production-ready system for managing pharmaceutical services in resource-limited settings. Enables seamless data synchronization between OpenMRS installations, health facilities, and community pharmacies.

### Key Features

✅ **Multi-Component Architecture**
- Desktop pharmacy application (PyQt6)
- Central web server (Express.js + PostgreSQL)
- OpenMRS synchronization module

✅ **Advanced Form Engine**
- OpenMRS-compatible JSON forms
- Conditional logic and validation
- Dynamic field behavior

✅ **Professional Security**
- Role-based access control
- JWT authentication
- Audit logging
- Encrypted data transmission

✅ **Offline-First**
- Pharmacy app works offline
- Automatic sync when connected
- Conflict resolution

✅ **Scalable Architecture**
- Designed for millions of patients
- Multi-region ready
- High availability
- Database replication

---

## 📋 System Components

### 1. Python Pharmacy Application

**Desktop application for pharmacists to manage drug dispensing**

```
python-pharmacy-app/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── config/                          # Configuration files
│   ├── settings.py                 # Environment-based settings
│   └── constants.py                # Application constants
├── database/                        # SQLite database layer
│   ├── models.py                   # Data models
│   ├── db_manager.py               # Database operations
│   └── complete_models.py          # Extended models
├── forms/                           # Form handling
│   ├── form_engine.py              # JSON form renderer
│   ├── enhanced_form_engine.py     # Advanced form features
│   ├── validators.py               # Field validation
│   └── condition_evaluator.py      # Conditional logic
├── services/                        # External integrations
│   └── api_client.py               # Central server API client
├── ui/                             # PyQt6 user interface
│   ├── main_window.py              # Main application window
│   ├── login_window.py             # Authentication
│   ├── clients_view.py             # Clients list
│   ├── client_details_view.py      # Client details
│   ├── form_view.py                # Form filling
│   ├── admin_panel.py              # Admin settings
│   ├── styles.py                   # UI styling
│   └── dialogs/                    # Dialog windows
├── utils/                          # Utility functions
│   ├── logger.py                   # Application logging
│   ├── validators.py               # Data validators
│   └── helpers.py                  # Helper functions
└── README.md                       # Local documentation
```

**Features:**
- Authenticate and manage users
- Download and manage clients from central server
- View detailed client information
- Fill dynamic OpenMRS-style forms
- Save drafts and submit forms
- Sync data automatically
- Work offline with automatic sync

---

### 2. React Backend Server

**Central Node.js/Express server for data management**

```
react-backend-server/
├── src/
│   ├── server.js                   # Express server setup
│   ├── config/
│   │   ├── database.js             # Database connection
│   │   └── logger.js               # Logging configuration
│   ├── models/
│   │   └── index.js                # Sequelize models
│   ├── routes/
│   │   ├── auth.js                 # Authentication endpoints
│   │   ├── clients.js              # Client management
│   │   ├── forms.js                # Form management
│   │   ├── submissions.js          # Form submissions
│   │   ├── pharmacies.js           # Pharmacy management
│   │   ├── facilities.js           # Facility management
│   │   └── sync.js                 # Sync operations
│   ├── middleware/
│   │   ├── auth.js                 # JWT authentication
│   │   └── errorHandler.js         # Error handling
│   └── services/
│       ├── sync-manager.js         # Sync orchestration
│       └── email-service.js        # Email notifications
├── package.json                    # Node dependencies
├── .env.example                    # Environment template
└── README.md                       # Documentation
```

**Features:**
- User authentication and authorization
- Client data management
- Form definition and versioning
- Form submission handling
- Pharmacy and facility management
- Sync coordination
- Audit logging

---

### 3. OpenMRS Sync Module

**Scheduled service for bidirectional sync with OpenMRS**

```
OpenMRS-Sync-Module/
├── openmrs-sync-manager.js         # Main sync service
├── package.json                    # Dependencies
├── .env.example                    # Configuration template
└── README.md                       # Documentation
```

**Features:**
- Pull form submissions from central server
- Create OpenMRS encounters from submissions
- Map form fields to OpenMRS concepts
- Pull patient updates from OpenMRS
- Confirm sync back to central server
- Error handling and retry logic
- Configurable sync intervals

---

## 🚀 Quick Start

### Prerequisites

- **For Python App:**
  - Python 3.8 or higher
  - PyQt6
  - SQLite3

- **For Backend Server:**
  - Node.js 14+
  - PostgreSQL 12+
  - npm or yarn

- **For OpenMRS Sync:**
  - Node.js 14+
  - OpenMRS 2.x instance
  - FHIR module installed

### Installation

#### 1. Python Pharmacy App

```bash
cd python-pharmacy-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure settings
cp .env.example .env
# Edit .env with your server URL

# Run application
python main.py
```

#### 2. React Backend Server

```bash
cd react-backend-server

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your database and server settings

# Set up database
npm run migrate

# Seed initial data (optional)
npm run seed

# Start development server
npm run dev

# Or start production server
npm start
```

#### 3. OpenMRS Sync Module

```bash
cd OpenMRS-Sync-Module

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with OpenMRS and central server credentials

# Start sync service
npm start

# Or run in development mode
npm run dev
```

---

## 📊 System Architecture

The system follows a three-tier architecture:

```
Health Facilities (OpenMRS)
        ↓
Central Sync Server (Express.js + PostgreSQL)
        ↓
Community Pharmacies (Python Desktop App)
```

**Data Flow:**

1. **Facility to Central:** Facilities upload client data to central server
2. **Central to Pharmacy:** Pharmacy app downloads clients and forms
3. **Pharmacy to Central:** Pharmacist completes forms, submissions sent to central server
4. **Central to OpenMRS:** Form submissions synced as OpenMRS encounters
5. **OpenMRS to Central:** Patient updates pulled and distributed back to pharmacies

See [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) for detailed architecture documentation.

---

## 📚 API Documentation

Complete API documentation available in [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

### Key Endpoints

**Authentication**
```
POST   /api/auth/signup           # Register new user
POST   /api/auth/login            # Authenticate
POST   /api/auth/verify           # Verify token
```

**Clients**
```
GET    /api/clients               # List all clients
GET    /api/clients/:id           # Get client details
POST   /api/clients               # Create/upload client
POST   /api/clients/bulk/upload   # Bulk upload
PUT    /api/clients/:id           # Update client
```

**Forms**
```
GET    /api/forms                 # List available forms
GET    /api/forms/:id             # Get form definition
POST   /api/forms/upload          # Upload new form
PUT    /api/forms/:id             # Update form
```

**Submissions**
```
POST   /api/submissions/submit    # Submit form
POST   /api/submissions/save-draft # Save as draft
GET    /api/submissions/:id       # Get submission
PATCH  /api/submissions/:id/status # Update status
```

**Sync**
```
GET    /api/sync/status           # Get sync status
GET    /api/sync/logs             # Get sync logs
POST   /api/sync/pharmacy/pull-clients   # Pharmacy pulls clients
POST   /api/sync/openmrs/pull-submissions # OpenMRS pulls submissions
```

---

## 🔐 Security Features

- ✅ JWT token-based authentication
- ✅ Role-based access control (RBAC)
- ✅ Data encryption in transit (HTTPS/TLS)
- ✅ Database connection encryption
- ✅ Audit logging of all operations
- ✅ Rate limiting (100 requests/15 min)
- ✅ CORS security headers
- ✅ Input validation and sanitization
- ✅ SQL injection prevention
- ✅ XSS protection

---

## 📱 User Roles

### Admin
- Upload and manage forms
- Create and manage users
- Manage pharmacies and facilities
- View system statistics
- Configure system settings

### Pharmacy Staff
- View assigned clients
- Fill and submit forms
- View form history
- Sync data
- Manage personal account

### Facility Manager
- Assign clients to pharmacies
- Manage facility settings
- View client assignments
- Export client data

### OpenMRS Sync (Automated)
- Pull form submissions
- Create OpenMRS encounters
- Sync patient updates
- Confirm sync operations

---

## 🗄️ Database Schema

### Python Pharmacy App (SQLite)
- Users
- Clients
- Forms
- Form Submissions
- Sync Logs

### Central Server (PostgreSQL)
- Users
- Clients
- Pharmacies
- Facilities
- Forms
- Form Submissions
- Sync Logs
- Audit Logs

See [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md#database-schema) for detailed schema.

---

## 🔄 Sync Strategy

### Periodic Sync (Default: Every 5 minutes)

1. **Pharmacy App Sync**
   - Check for new clients
   - Download latest forms
   - Upload form submissions
   - Receive updates

2. **OpenMRS Sync Module**
   - Pull pending submissions
   - Create OpenMRS encounters
   - Pull patient updates
   - Confirm sync

3. **Error Handling**
   - Automatic retry (up to 3 attempts)
   - Exponential backoff
   - Error logging
   - Admin notifications

---

## 📊 Data Models

### Client
```json
{
  "pepfarId": "KE-001-001-001",
  "fullName": "John Doe",
  "dob": "1990-05-15",
  "gender": "M",
  "phone": "0712345678",
  "email": "john@example.com",
  "facility": "Central Hospital",
  "hivStatus": "Positive",
  "cd4Count": "450",
  "viralLoad": "Undetectable",
  "status": "Active"
}
```

### Form
```json
{
  "id": "FORM-001",
  "name": "ARV Refill Form",
  "version": 1,
  "sections": [
    {
      "name": "Patient Info",
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
}
```

### Form Submission
```json
{
  "formId": "FORM-001",
  "clientId": "client-uuid",
  "status": "submitted",
  "fields": {
    "drug_name": "Efavirenz",
    "quantity": 30
  },
  "submittedAt": "2024-01-21T12:00:00Z"
}
```

---

## 🛠️ Development

### Project Structure

```
compharm/
├── python-pharmacy-app/        # Desktop application
├── react-backend-server/       # Backend server
├── OpenMRS-Sync-Module/        # Sync service
├── API_DOCUMENTATION.md        # API reference
├── SYSTEM_ARCHITECTURE.md      # Architecture details
├── Adverse Drug Reaction Form.json    # Sample forms
└── Combined Pharmacy Order Form.json  # Sample forms
```

### Development Workflow

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd compharm
   ```

2. **Set up each component** (see Quick Start above)

3. **Make changes and test**
   ```bash
   # Python app
   cd python-pharmacy-app
   python main.py

   # Backend server
   cd react-backend-server
   npm run dev

   # Sync module
   cd OpenMRS-Sync-Module
   npm run dev
   ```

4. **Run tests**
   ```bash
   # Backend tests
   cd react-backend-server
   npm test

   # Sync module tests
   cd OpenMRS-Sync-Module
   npm test
   ```

---

## 📋 Configuration

### Environment Variables

#### Python App
```bash
CENTRAL_SERVER_URL=http://localhost:3001/api
SYNC_INTERVAL=5
AUTO_SYNC_ENABLED=true
DATABASE_PATH=~/.pharmacy/pharmacy.db
LOG_LEVEL=INFO
```

#### Backend Server
```bash
PORT=3001
NODE_ENV=development
DB_HOST=localhost
DB_NAME=pharmacy_sync
DB_USER=postgres
DB_PASSWORD=postgres
JWT_SECRET=your-secret-key
OPENMRS_SERVER_URL=http://localhost:8080/openmrs
```

#### Sync Module
```bash
CENTRAL_SERVER_URL=http://localhost:3001/api
OPENMRS_SERVER_URL=http://localhost:8080/openmrs
SYNC_INTERVAL_MINUTES=5
ENABLE_DETAILED_LOGGING=true
```

---

## 🧪 Testing

### Run Tests

```bash
# Backend API tests
cd react-backend-server
npm test

# Python app tests (if available)
cd python-pharmacy-app
pytest

# Sync module tests
cd OpenMRS-Sync-Module
npm test
```

---

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access services
# - Backend: http://localhost:3001
# - OpenMRS: http://localhost:8080/openmrs
```

### Production Checklist

- [ ] Set strong JWT secret
- [ ] Configure HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure email for notifications
- [ ] Set up monitoring and alerting
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Test disaster recovery
- [ ] Document deployment procedure
- [ ] Set up CI/CD pipeline

---

## 📖 Documentation

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [System Architecture](SYSTEM_ARCHITECTURE.md) - Detailed architecture
- [Python App README](python-pharmacy-app/README.md) - Desktop app guide
- [Backend Server](react-backend-server/README.md) - Server setup
- [Sync Module](OpenMRS-Sync-Module/README.md) - Sync configuration

---

## 🤝 Contributing

### Development Guidelines

1. Follow existing code style
2. Write tests for new features
3. Update documentation
4. Create feature branches
5. Submit pull requests with clear descriptions

### Code Style

- **Python:** PEP 8
- **JavaScript:** ESLint config
- **SQL:** Standard conventions

---

## 🐛 Troubleshooting

### Common Issues

**Pharmacy app won't connect to server**
- Check server URL in settings
- Verify backend server is running
- Check firewall/network connectivity
- Review application logs

**Form submissions not syncing**
- Verify internet connection
- Check sync interval setting
- Review OpenMRS sync logs
- Check for validation errors

**Database connection errors**
- Verify PostgreSQL is running
- Check credentials in .env
- Verify database exists
- Check connection pool settings

**OpenMRS sync failures**
- Verify OpenMRS server URL
- Check OpenMRS credentials
- Verify FHIR module installed
- Review sync module logs

---

## 📞 Support

- **Documentation:** See docs in repository
- **Issues:** Report via GitHub Issues
- **Email:** support@pharmacy.com
- **Status Page:** https://status.pharmacy.com

---

## 📄 License

MIT License - See LICENSE file for details

---

## ✨ Acknowledgments

Built with:
- PyQt6 - Desktop UI framework
- Express.js - Web server
- PostgreSQL - Database
- OpenMRS - Clinical data
- Node.js - JavaScript runtime

---

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core system architecture
- ✅ Desktop pharmacy app
- ✅ Central server
- ✅ OpenMRS sync

### Phase 2
- [ ] Mobile app (React Native)
- [ ] Advanced analytics
- [ ] Machine learning predictions
- [ ] Multi-language support

### Phase 3
- [ ] Blockchain integration
- [ ] Decentralized sync
- [ ] Advanced security features
- [ ] Global scale deployment

---

**Last Updated:** January 21, 2024
**Version:** 1.0.0
**Status:** Production Ready
