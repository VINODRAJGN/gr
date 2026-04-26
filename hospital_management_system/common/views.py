from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from patients.models import Patient
from doctors.models import Doctor, Prescription
from appointments.models import Appointment
from .models import UserProfile
from datetime import date, datetime, timedelta

def home(request):
    total_doctors = Doctor.objects.filter(is_active=True).count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    return render(request, 'home.html', {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
    })

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'patient')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name
        )
        UserProfile.objects.create(user=user, role=role, phone=phone, address=address)

        if role == 'patient':
            age = request.POST.get('age', 0)
            gender = request.POST.get('gender', 'Male')
            blood_group = request.POST.get('blood_group', '')
            Patient.objects.create(
                user=user, age=age, gender=gender,
                blood_group=blood_group, phone=phone, address=address
            )
        elif role == 'doctor':
            from doctors.models import Specialization
            spec_id = request.POST.get('specialization')
            spec = Specialization.objects.filter(id=spec_id).first()
            exp = request.POST.get('experience_years', 0)
            qual = request.POST.get('qualification', '')
            Doctor.objects.create(
                user=user, specialization=spec, phone=phone,
                address=address, experience_years=exp, qualification=qual
            )

        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    from doctors.models import Specialization
    specializations = Specialization.objects.all()
    return render(request, 'register.html', {'specializations': specializations})

def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect_by_role(user)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def redirect_by_role(user):
    profile = UserProfile.objects.filter(user=user).first()
    if user.is_superuser or (profile and profile.role == 'admin'):
        return redirect('admin_dashboard')
    elif profile and profile.role == 'doctor':
        return redirect('doctor_dashboard')
    elif profile and profile.role == 'appointment_manager':
        return redirect('appointment_manager_dashboard')
    else:
        return redirect('patient_dashboard')

@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def admin_dashboard(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not (request.user.is_superuser or (profile and profile.role == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('home')
    today = date.today()
    doctors = Doctor.objects.select_related('user','specialization').all()
    patients = Patient.objects.select_related('user').all()
    today_appointments = Appointment.objects.filter(appointment_date=today).select_related('patient__user','doctor__user')
    pending_appointments = Appointment.objects.filter(status='pending').count()
    recent_appointments = Appointment.objects.select_related('patient__user','doctor__user').order_by('-created_at')[:10]
    return render(request, 'admin/dashboard.html', {
        'doctors': doctors,
        'patients': patients,
        'today_appointments': today_appointments,
        'total_doctors': doctors.count(),
        'total_patients': patients.count(),
        'total_appointments': Appointment.objects.count(),
        'pending_appointments': pending_appointments,
        'recent_appointments': recent_appointments,
    })

@login_required
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    today = date.today()
    today_appointments = Appointment.objects.filter(
        doctor=doctor, appointment_date=today
    ).select_related('patient__user').order_by('appointment_time')
    upcoming = Appointment.objects.filter(
        doctor=doctor, appointment_date__gte=today, status__in=['pending','confirmed']
    ).select_related('patient__user').order_by('appointment_date','appointment_time')[:10]
    prescriptions = Prescription.objects.filter(doctor=doctor).select_related('patient__user').order_by('-created_at')[:10]
    return render(request, 'doctor/dashboard.html', {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'upcoming': upcoming,
        'prescriptions': prescriptions,
        'total_patients': Appointment.objects.filter(doctor=doctor).values('patient').distinct().count(),
    })

@login_required
def patient_dashboard(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    today = date.today()
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor__user','doctor__specialization').order_by('-appointment_date')
    upcoming = appointments.filter(appointment_date__gte=today, status__in=['pending','confirmed'])
    prescriptions = Prescription.objects.filter(patient=patient).select_related('doctor__user').order_by('-created_at')
    # Check for late appointments to show notification
    late_appointments = []
    for appt in upcoming:
        appt_dt = datetime.combine(appt.appointment_date, appt.appointment_time)
        if datetime.now() > appt_dt - timedelta(minutes=30) and not appt.notification_sent:
            late_appointments.append(appt)
    return render(request, 'patient/dashboard.html', {
        'patient': patient,
        'appointments': appointments[:10],
        'upcoming': upcoming,
        'prescriptions': prescriptions[:5],
        'late_appointments': late_appointments,
    })

@login_required
def appointment_manager_dashboard(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not (profile and profile.role in ['appointment_manager', 'admin']) and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('home')
    today = date.today()
    all_appointments = Appointment.objects.select_related(
        'patient__user','doctor__user','doctor__specialization'
    ).order_by('appointment_date','appointment_time')
    today_appointments = all_appointments.filter(appointment_date=today)
    pending = all_appointments.filter(status='pending')
    return render(request, 'manager/dashboard.html', {
        'all_appointments': all_appointments[:20],
        'today_appointments': today_appointments,
        'pending': pending,
        'total': all_appointments.count(),
    })
