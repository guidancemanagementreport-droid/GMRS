# Guidance Management Reporting System (GMRS) - Project Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Dependencies & Libraries](#dependencies--libraries)
4. [Project Architecture](#project-architecture)
5. [Database Schema](#database-schema)
6. [Authentication System](#authentication-system)
7. [Frontend Technologies](#frontend-technologies)
8. [Deployment](#deployment)
9. [Environment Variables](#environment-variables)
10. [File Structure](#file-structure)

---

## Overview

**GMRS (Guidance Management Reporting System)** is a comprehensive web application designed for managing guidance office operations, student reports, counseling requests, and case management. The system supports multiple user roles with role-based access control and provides a secure, responsive interface for all users.

---

## Technology Stack

### Backend Framework
- **Flask 3.0.0** - Python web framework
  - Used for routing, templating, and session management
  - Blueprint-based architecture for modular routing
  - WSGI application for server deployment

### Database & Backend Services
- **Supabase** - Backend-as-a-Service (BaaS)
  - **PostgreSQL Database** - Primary database
  - **Row Level Security (RLS)** - Fine-grained access control
  - **Service Role Key** - For privileged operations (admin, login)
  - **Anon Key** - For regular user operations

### Authentication
- **Custom Authentication System**
  - **bcrypt 4.1.2** - Password hashing library
  - Flask sessions for user state management
  - Role-based access control (RBAC)

### Deployment Platform
- **Vercel** - Serverless deployment platform
  - Python serverless functions
  - Static file serving
  - Environment variable management

---

## Dependencies & Libraries

### Python Dependencies (`requirements.txt`)
```
Flask==3.0.0              # Web framework
supabase==2.3.0           # Supabase Python client
python-dotenv==1.0.0      # Environment variable management
Werkzeug==3.0.1           # WSGI utilities (Flask dependency)
bcrypt==4.1.2             # Password hashing
```

### Frontend Libraries (CDN)
- **Font Awesome 6.4.0** - Icon library
  - CDN: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css`
  - Used for navigation icons, dashboard icons, and UI elements

- **Toastify.js** - Toast notification library
  - CDN: `https://cdn.jsdelivr.net/npm/toastify-js`
  - CSS: `https://cdn.jsdelivr.net/npm/toastify-js/src/toastify.min.css`
  - Used for user feedback (success/error messages)

### Core Technologies
- **HTML5** - Markup language
- **CSS3** - Styling (custom stylesheet)
- **JavaScript (ES6+)** - Client-side scripting
- **Jinja2** - Template engine (Flask's default)

---

## Project Architecture

### Application Structure
```
GMRS/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── routes/                  # Route blueprints
│   │   ├── auth.py              # Authentication routes
│   │   ├── student.py           # Student routes
│   │   ├── teacher.py           # Teacher routes
│   │   ├── counselor.py         # Counselor routes
│   │   ├── admin.py             # Admin routes
│   │   ├── guest.py             # Guest/Applicant routes
│   │   ├── anonymous.py         # Anonymous reporting routes
│   │   └── main.py              # Public/main routes
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # Base template (with topbar)
│   │   ├── auth_base.html       # Auth pages template (no topbar)
│   │   ├── dashboard_base.html  # Dashboard template (with sidebar)
│   │   ├── auth/                # Authentication pages
│   │   ├── main/                # Public pages
│   │   ├── student/             # Student dashboard pages
│   │   ├── teacher/             # Teacher dashboard pages
│   │   ├── counselor/           # Counselor dashboard pages
│   │   ├── admin/               # Admin dashboard pages
│   │   ├── guest/               # Guest dashboard pages
│   │   └── anonymous/           # Anonymous pages
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   │   └── style.css        # Main stylesheet
│   │   └── js/
│   │       └── main.js          # Main JavaScript
│   └── utils/                   # Utility modules
│       └── auth.py              # Authentication decorators
├── api/                         # Vercel serverless entry point
│   ├── __init__.py
│   └── index.py                 # WSGI handler for Vercel
├── database/                    # Database SQL files
│   ├── schema.sql               # Complete database schema
│   ├── users_table.sql          # Users table only
│   ├── other_tables.sql         # All other tables
│   ├── admin_account.sql        # Default admin account
│   ├── fix_users_rls.sql        # RLS policy fixes
│   └── sample_data.sql          # Sample data (if any)
├── app.py                       # Local development entry point
├── requirements.txt             # Python dependencies
├── vercel.json                  # Vercel deployment config
└── README.md                    # Project README
```

### Blueprint Architecture
The application uses Flask blueprints for modular routing:
- `/auth` - Authentication (login, logout)
- `/student` - Student dashboard and features
- `/teacher` - Teacher dashboard and features
- `/counselor` - Counselor dashboard and features
- `/admin` - Admin dashboard and management
- `/guest` - Guest/Applicant features
- `/anonymous` - Anonymous reporting
- `/` - Public/main routes

---

## Database Schema

### Database: PostgreSQL (via Supabase)

### Main Tables

#### 1. `users` Table
- **Purpose**: User accounts and profiles
- **Key Fields**:
  - `id` (UUID) - Primary key
  - `user_id` (VARCHAR) - Unique identifier (student/teacher/counselor/admin ID)
  - `username` (VARCHAR) - Login username
  - `password_hash` (TEXT) - bcrypt hashed password
  - `role` (VARCHAR) - User role: 'student', 'teacher', 'counselor', 'admin'
  - `is_active` (BOOLEAN) - Account status
  - Profile fields: `first_name`, `last_name`, `email`, `contact_number`, etc.

#### 2. `reports` Table
- **Purpose**: Student and anonymous reports
- **Key Fields**: Report details, status, priority, assigned counselor

#### 3. `cases` Table
- **Purpose**: Case management
- **Key Fields**: Case details, status, assigned counselor, related report

#### 4. `case_notes` Table
- **Purpose**: Case notes and documentation
- **Key Fields**: Note content, case reference, author, timestamp

#### 5. `counseling_requests` Table
- **Purpose**: Counseling session requests
- **Key Fields**: Request details, student, status, scheduled date

#### 6. `guidance_requests` Table
- **Purpose**: Guidance service requests (for guests/applicants)
- **Key Fields**: Request type, status, applicant details

#### 7. `notifications` Table
- **Purpose**: User notifications
- **Key Fields**: Message, recipient, read status, timestamp

#### 8. `resources` Table
- **Purpose**: Resource library
- **Key Fields**: Title, description, category, file URL, visibility

#### 9. `exam_schedule` Table
- **Purpose**: Exam scheduling
- **Key Fields**: Exam details, date, time, location

#### 10. `system_settings` Table
- **Purpose**: System configuration
- **Key Fields**: Setting key, value, description

#### 11. `analytics_logs` Table
- **Purpose**: Access and activity logs
- **Key Fields**: User, action, timestamp, IP address

### Database Extensions
- **uuid-ossp** - UUID generation
- **moddatetime** - Automatic timestamp updates

### Row Level Security (RLS)
- Enabled on all tables
- Policies for:
  - Admin access (full CRUD)
  - User self-access (view/update own profile)
  - Role-based access (teachers view students, counselors view cases, etc.)
  - Anonymous access (for anonymous reporting)

---

## Authentication System

### Authentication Flow
1. **Login Process**:
   - User submits username and password
   - Backend queries `users` table using `username`
   - Password verified using `bcrypt.checkpw()`
   - Flask session created with user data
   - Redirect to role-specific dashboard

2. **Session Management**:
   - Flask sessions store: `user_id`, `user_role`, `user_name`, `username`
   - Session is permanent (`session.permanent = True`)
   - Session cleared on logout

3. **Password Hashing**:
   - Passwords hashed using `bcrypt` (bcrypt 4.1.2)
   - Stored as `password_hash` in database
   - Default admin password: `Admin123!` (hashed)

4. **Access Control**:
   - Decorator `@require_login` in `app/utils/auth.py`
   - Checks session for `user_id`
   - Redirects to login if not authenticated

### Supabase Client Configuration
- **Anon Key Client** (`app.supabase`): Regular operations
- **Service Role Key Client** (`app.supabase_admin`): 
  - Bypasses RLS policies
  - Used for login queries
  - Used for admin operations (user creation, etc.)

---

## Frontend Technologies

### CSS Features
- **Custom CSS** (`app/static/css/style.css`)
- **Responsive Design**: Mobile-first approach
- **Glassmorphism**: Modern UI effects
- **Gradient Backgrounds**: Color-coded by user role
- **Animations**: Logo rotation, hover effects, transitions
- **Mobile Menu**: Hamburger menu with overlay

### JavaScript Features
- **Vanilla JavaScript** (no frameworks)
- **Mobile Menu Toggle**: Hamburger menu functionality
- **Active Tab Detection**: URL-based active tab highlighting
- **Session Storage**: Persist active tab state
- **Form Validation**: Client-side validation
- **Toastify Integration**: Toast notifications
- **AJAX Requests**: Form submissions without page reload

### Template System
- **Jinja2 Templates**:
  - `base.html` - Main template with topbar navigation
  - `auth_base.html` - Auth pages (no topbar)
  - `dashboard_base.html` - Dashboard pages (with sidebar)
  - Role-specific templates in respective folders

### UI Components
- **Navigation Bar**: Topbar with logo, menu items, login/logout button
- **Sidebar**: Dashboard sidebar with role-specific links
- **Cards**: Dashboard stat cards and feature cards
- **Forms**: Modern form design with icons
- **Tables**: Data tables for reports, cases, etc.
- **Modals**: (If implemented) For confirmations, etc.

---

## Deployment

### Vercel Configuration

#### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

#### Serverless Entry Point
- **File**: `api/index.py`
- **Purpose**: WSGI handler for Vercel
- **Function**: Exports Flask app for serverless execution

### Deployment Steps
1. Connect GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch
4. Static files served by Flask (no custom routing needed)

### Local Development
```bash
# Run locally
python app.py

# Or with Flask CLI
flask run
```

---

## Environment Variables

### Required Environment Variables

#### For Local Development (`.env` file)
```env
SECRET_KEY=your-secret-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

#### For Vercel Deployment
Set in Vercel Dashboard → Project Settings → Environment Variables:
- `SECRET_KEY` - Flask session secret key
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon/public key
- `SUPABASE_SERVICE_KEY` - Supabase service role key (for admin operations)

### Environment Variable Usage
- Accessed via `os.environ.get()` in `app/__init__.py`
- Fallback values provided for development
- **Never commit** `.env` file to Git

---

## File Structure

### Key Files Explained

#### `app/__init__.py`
- Flask application factory
- Supabase client initialization (anon + service role)
- Blueprint registration
- Static folder configuration for Vercel

#### `app/routes/auth.py`
- `/auth/login` - POST: Login handler
- `/auth/logout` - GET: Logout handler
- Uses `supabase_admin` for login queries (bypasses RLS)
- Sets Flask session on successful login
- Redirects to role-specific dashboard

#### `app/routes/student.py`
- Student dashboard routes
- Report submission
- Counseling requests
- Profile management
- Resources access

#### `app/routes/teacher.py`
- Teacher dashboard routes
- Report review
- Incident submission
- Case monitoring

#### `app/routes/counselor.py`
- Counselor dashboard routes
- Case management
- Case notes
- Student history
- Analytics

#### `app/routes/admin.py`
- Admin dashboard routes
- User management (create, update, delete)
- System settings
- Analytics
- Backup/restore

#### `app/utils/auth.py`
- `@require_login` decorator
- Checks Flask session for authentication
- Redirects to login if not authenticated

#### `app/static/css/style.css`
- All application styles
- Responsive breakpoints
- Role-specific color schemes
- Animations and transitions

#### `app/static/js/main.js`
- Mobile menu functionality
- Active tab detection
- Form handling
- Toastify integration

#### `database/schema.sql`
- Complete database schema
- Table definitions
- Indexes
- RLS policies
- Triggers for auto-updating timestamps

---

## User Roles & Access

### 1. Student
- **Color Theme**: Green
- **Access**: Own reports, counseling requests, profile, resources

### 2. Guest/Applicant
- **Color Theme**: Orange
- **Access**: Guidance requests, exam schedule, profile

### 3. Teacher
- **Color Theme**: Blue
- **Access**: Review student reports, submit incidents, monitor cases

### 4. Counselor
- **Color Theme**: Red
- **Access**: Assigned cases, case notes, student history, analytics

### 5. Admin
- **Color Theme**: Purple
- **Access**: Full system access, user management, system settings

### 6. Anonymous
- **Access**: Submit anonymous reports, track report status (no login required)

---

## Security Features

1. **Password Hashing**: bcrypt with salt
2. **Row Level Security**: Supabase RLS policies
3. **Session Management**: Flask secure sessions
4. **Role-Based Access**: Decorators and route protection
5. **Service Role Key**: Separate key for privileged operations
6. **Input Validation**: Client and server-side validation
7. **SQL Injection Protection**: Supabase client handles parameterization

---

## Development Notes

### Adding New Routes
1. Create route function in appropriate blueprint file
2. Add `@require_login` decorator if authentication needed
3. Create template in appropriate folder
4. Update navigation/sidebar if needed

### Adding New Database Tables
1. Create SQL in `database/schema.sql`
2. Add RLS policies
3. Add indexes for performance
4. Add triggers if needed (e.g., auto-update timestamps)
5. Run SQL in Supabase SQL Editor

### Styling Guidelines
- Use role-specific color variables
- Follow mobile-first responsive design
- Use Font Awesome icons
- Implement hover effects and transitions

---

## Troubleshooting

### Common Issues

1. **Login 401 Error**
   - Check Supabase credentials
   - Verify `SUPABASE_SERVICE_KEY` is set
   - Check RLS policies allow login queries

2. **BuildError (URL endpoint)**
   - Verify route name matches `url_for()` call
   - Check blueprint is registered
   - Ensure route function exists

3. **Static Files Not Loading (Vercel)**
   - Verify static files are in Git
   - Check `static_folder` path in `app/__init__.py`
   - Ensure Flask handles static files (no custom routing)

4. **RLS Policy Recursion**
   - Use `SECURITY DEFINER` functions
   - Avoid policies that query the same table
   - Use service role key for admin operations

---

## Version Information

- **Flask**: 3.0.0
- **Supabase Python Client**: 2.3.0
- **bcrypt**: 4.1.2
- **Python**: 3.8+ (recommended 3.11+)
- **PostgreSQL**: (via Supabase)

---

## Additional Resources

- **Supabase Documentation**: https://supabase.com/docs
- **Flask Documentation**: https://flask.palletsprojects.com/
- **Vercel Python Documentation**: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- **bcrypt Documentation**: https://github.com/pyca/bcrypt/

---

**Last Updated**: December 2024
**Project Status**: Active Development

