# Guidance Management Reporting System (GMRS)

A comprehensive Flask-based web application for managing guidance office operations, student reports, counseling requests, and case management.

## Features

- **6 User Types**: Student, Guest/Applicant, Teacher, Counselor, System Admin, and Anonymous Reporter
- **Color-Coded Dashboards**: Each user type has a distinct color scheme for easy identification
- **Role-Based Access Control**: Secure authentication and authorization
- **Responsive Design**: Mobile-first, fully responsive UI
- **Anonymous Reporting**: Secure anonymous report submission
- **Case Management**: Comprehensive case tracking and notes system
- **Analytics & Reporting**: Statistical insights and reporting tools

## Tech Stack

- **Backend**: Python Flask
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage
- **Frontend**: HTML5, CSS3, JavaScript

## Installation

### Prerequisites

- Python 3.8 or higher
- Supabase account and project
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GMRS
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Supabase**
   - Create a new project at [supabase.com](https://supabase.com)
   - Go to Settings > API to get your project URL and anon key
   - Run the SQL schema from `database/schema.sql` in your Supabase SQL Editor

5. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key-here
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Database Schema

The database includes the following main tables:

- `users` - User accounts and profiles
- `reports` - Student and anonymous reports
- `cases` - Case management
- `case_notes` - Case notes and documentation
- `counseling_requests` - Counseling session requests
- `guidance_requests` - Guidance service requests
- `notifications` - User notifications
- `resources` - Resource library
- `exam_schedule` - Exam scheduling
- `system_settings` - System configuration
- `analytics_logs` - Access and activity logs

## User Roles & Dashboards

### 🟩 Student Dashboard (Green)
- Submit Report
- Profile Management
- View Report Status
- Request Counseling
- View Counseling Status
- Help/Support
- Notifications
- Guidance Resources

### 🟧 Guest/Applicant Dashboard (Orange)
- Submit Guidance Request
- View Guidance Status
- Exam Schedule
- Notifications
- Guidance Resources

### 🟦 Teacher Dashboard (Blue)
- Student Reports Review
- Submit Incident Report
- Communication Tools
- Notifications
- Profile Management
- Monitor Case Progress

### 🟥 Counselor Dashboard (Red)
- Assigned Cases
- Case Notes
- Notifications
- Student History
- Resource Library
- View Statistical Report
- Profile Management
- Analytics
- Manage Guidance & Counseling

### 🟪 System Admin Dashboard (Purple)
- User Management
- Report Analytics
- System Settings
- Manage All Users
- Backup & Restore
- Security & Access Control
- Notifications
- Profile Management

### Anonymous Reporter
- Submit anonymous reports without login
- Track report status using report ID

## Project Structure

```
GMRS/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes/              # Route blueprints
│   │   ├── auth.py         # Authentication routes
│   │   ├── student.py      # Student routes
│   │   ├── guest.py        # Guest routes
│   │   ├── teacher.py      # Teacher routes
│   │   ├── counselor.py    # Counselor routes
│   │   ├── admin.py        # Admin routes
│   │   ├── anonymous.py    # Anonymous routes
│   │   └── main.py         # Main/public routes
│   ├── templates/          # HTML templates
│   │   ├── base.html       # Base template
│   │   ├── main/           # Public pages
│   │   ├── auth/           # Auth pages
│   │   ├── student/        # Student pages
│   │   ├── guest/          # Guest pages
│   │   ├── teacher/        # Teacher pages
│   │   ├── counselor/      # Counselor pages
│   │   ├── admin/          # Admin pages
│   │   └── anonymous/      # Anonymous pages
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css   # Main stylesheet
│   │   └── js/
│   │       └── main.js     # Main JavaScript
│   └── utils/
│       └── auth.py         # Authentication utilities
├── database/
│   └── schema.sql          # Database schema
├── app.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## API Endpoints

### Authentication
- `GET/POST /auth/login` - User login
- `GET/POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Student Routes
- `GET /student/dashboard` - Student dashboard
- `GET/POST /student/submit-report` - Submit report
- `GET /student/report-status` - View report status
- `GET/POST /student/request-counseling` - Request counseling
- `GET /student/counseling-status` - View counseling status
- `GET/POST /student/profile` - Profile management

### Guest Routes
- `GET /guest/dashboard` - Guest dashboard
- `GET/POST /guest/submit-request` - Submit guidance request
- `GET /guest/request-status` - View request status
- `GET /guest/exam-schedule` - View exam schedule
- `GET/POST /guest/profile` - Profile management

### Teacher Routes
- `GET /teacher/dashboard` - Teacher dashboard
- `GET /teacher/reports` - Review student reports
- `GET/POST /teacher/submit-incident` - Submit incident report
- `GET /teacher/cases` - Monitor case progress
- `GET/POST /teacher/profile` - Profile management

### Counselor Routes
- `GET /counselor/dashboard` - Counselor dashboard
- `GET /counselor/cases` - View assigned cases
- `GET/POST /counselor/case/<id>/notes` - Manage case notes
- `GET /counselor/student-history/<id>` - View student history
- `GET /counselor/analytics` - View analytics
- `GET/POST /counselor/manage-guidance` - Manage resources
- `GET/POST /counselor/profile` - Profile management

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - User management
- `PUT/DELETE /admin/users/<id>` - User actions
- `GET /admin/analytics` - Report analytics
- `GET/POST /admin/settings` - System settings
- `GET /admin/backup` - Backup management
- `GET /admin/security` - Security logs
- `GET/POST /admin/profile` - Profile management

### Anonymous Routes
- `GET/POST /anonymous/report` - Submit anonymous report
- `GET /anonymous/track/<id>` - Track report status

## Security Features

- Row Level Security (RLS) policies in Supabase
- Role-based access control
- Secure session management
- Input validation
- Anonymous reporting without authentication

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Creating Sample Data

You can create sample data directly in Supabase or through the application interface after logging in as an admin.

## Testing

1. Create test users for each role
2. Test each dashboard functionality
3. Verify role-based access control
4. Test anonymous reporting
5. Verify notifications system

## Deployment

### Recommended Deployment Options

1. **Heroku**: Easy deployment with PostgreSQL addon
2. **Railway**: Simple deployment with Supabase integration
3. **DigitalOcean**: App Platform with managed database
4. **AWS**: Elastic Beanstalk or EC2

### Environment Variables for Production

Make sure to set:
- `SECRET_KEY` - Strong random secret key
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `FLASK_ENV=production`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the repository.

## Acknowledgments

Built with Flask and Supabase for modern, scalable guidance office management.

