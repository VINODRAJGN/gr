"""
Run with: python manage.py shell < setup_data.py
This creates demo data for a fresh installation.
"""
from django.contrib.auth.models import User
from common.models import UserProfile
from patients.models import Patient
from doctors.models import Doctor, Specialization
from appointments.models import Appointment
from datetime import date, time

print("Creating demo data...")

# Admin
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@hospital.com', 'admin123', first_name='Admin', last_name='User')
    UserProfile.objects.create(user=admin, role='admin')
    print("  Admin created: admin / admin123")

# Specializations
specs = ['Cardiology', 'Orthopedics', 'Neurology', 'Dermatology', 'Pediatrics', 'General Medicine']
for s in specs:
    Specialization.objects.get_or_create(name=s)
print(f"  Specializations: {', '.join(specs)}")

# Doctors
doc_data = [
    ('doctor1', 'Ravi', 'Kumar', 'Cardiology', 10),
    ('doctor2', 'Priya', 'Sharma', 'Orthopedics', 8),
    ('doctor3', 'Anil', 'Verma', 'Neurology', 15),
    ('doctor4', 'Meena', 'Patel', 'Pediatrics', 6),
]
for username, fn, ln, spec, exp in doc_data:
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username, f'{username}@hospital.com', 'doctor123', first_name=fn, last_name=ln)
        UserProfile.objects.create(user=u, role='doctor')
        Doctor.objects.create(user=u, specialization=Specialization.objects.get(name=spec),
                              phone='9876500000', experience_years=exp, qualification='MBBS, MD',
                              available_from=time(9,0), available_to=time(17,0))
        print(f"  Doctor created: {username} / doctor123")

# Patients
pat_data = [
    ('patient1', 'Arjun', 'Singh', 28, 'Male', 'A+'),
    ('patient2', 'Sunita', 'Reddy', 35, 'Female', 'B+'),
    ('patient3', 'Rahul', 'Gupta', 22, 'Male', 'O+'),
]
patients = []
for username, fn, ln, age, gender, bg in pat_data:
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username, f'{username}@email.com', 'patient123', first_name=fn, last_name=ln)
        UserProfile.objects.create(user=u, role='patient')
        p = Patient.objects.create(user=u, age=age, gender=gender, blood_group=bg, phone='9876500001')
        patients.append(p)
        print(f"  Patient created: {username} / patient123")

# Manager
if not User.objects.filter(username='manager').exists():
    mgr = User.objects.create_user('manager', 'manager@hospital.com', 'manager123', first_name='Appointment', last_name='Manager')
    UserProfile.objects.create(user=mgr, role='appointment_manager')
    print("  Manager created: manager / manager123")

print("\nSetup complete! Visit http://127.0.0.1:8000/")
