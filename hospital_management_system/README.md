# MediCare - Hospital Management System

A fully functional Django-based Hospital Management System.

## Features

- **Role-based Access**: Admin, Doctor, Patient, Appointment Manager
- **Patient Management**: Add, edit, delete patients
- **Doctor Management**: Add, edit, delete doctors with specializations
- **Appointment System**: Booking, scheduling, queue management, priority levels
- **Prescriptions**: Doctors create digital prescriptions for patients
- **Late Appointment Notifications**: Patients get notified 30 minutes before appointments
- **Admin Dashboard**: Full overview of hospital operations

## Demo Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Doctor | doctor1 | doctor123 |
| Doctor | doctor2 | doctor123 |
| Patient | patient1 | patient123 |
| Patient | patient2 | patient123 |
| Appt. Manager | manager | manager123 |

## Setup Instructions

### 1. Install Python dependencies
```bash
pip install django
```

### 2. Navigate to project folder
```bash
cd hospital_management_system
```

### 3. Run migrations
```bash
python manage.py migrate
```

### 4. Create superuser (optional - demo admin already exists)
```bash
python manage.py createsuperuser
```

### 5. Load sample data (optional)
```bash
python manage.py shell < setup_data.py
```

### 6. Run the development server
```bash
python manage.py runserver
```

### 7. Open in browser
```
http://127.0.0.1:8000/
```

## Pages & Navigation

### Common Pages
- `/` — Home page
- `/login/` — Login
- `/register/` — Register as Patient, Doctor, or Appointment Manager

### Admin Pages
- `/dashboard/admin/` — Admin dashboard with stats
- `/doctors/` — Manage doctors
- `/doctors/add/` — Add new doctor
- `/patients/` — Manage patients
- `/patients/add/` — Add new patient
- `/appointments/` — All appointments
- `/appointments/queue/` — Today's queue

### Doctor Pages
- `/dashboard/doctor/` — Today's schedule, prescriptions
- `/prescriptions/add/` — Create prescription

### Patient Pages
- `/dashboard/patient/` — Appointments, prescriptions, notifications
- `/appointments/book/` — Book new appointment
- `/profile/` — Edit profile

### Appointment Manager Pages
- `/dashboard/manager/` — Overview
- `/appointments/schedule/` — Schedule appointment
- `/appointments/queue/` — Manage queue with priorities

## Project Structure

```
hospital_management_system/
├── hospital_management/     # Django project settings & URLs
├── common/                  # Auth views, home, dashboards
├── patients/                # Patient model & views
├── doctors/                 # Doctor, Prescription models & views
├── appointments/            # Appointment model & views
├── templates/               # All HTML templates
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── admin/
│   ├── doctor/
│   ├── patient/
│   └── manager/
└── manage.py
```
