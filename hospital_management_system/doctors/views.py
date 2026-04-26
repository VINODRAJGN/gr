from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Doctor, Prescription, Specialization
from common.models import UserProfile
from appointments.models import Appointment
from patients.models import Patient
from datetime import date

@login_required
def doctor_list(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not (request.user.is_superuser or (profile and profile.role == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('home')
    doctors = Doctor.objects.select_related('user','specialization').all()
    return render(request, 'admin/doctors.html', {'doctors': doctors})

@login_required
def add_doctor(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not (request.user.is_superuser or (profile and profile.role == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('home')
    specializations = Specialization.objects.all()
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password', 'doctor123')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        spec_id = request.POST.get('specialization')
        exp = request.POST.get('experience_years', 0)
        qual = request.POST.get('qualification', '')
        avail_from = request.POST.get('available_from', '09:00')
        avail_to = request.POST.get('available_to', '17:00')
        spec_new = request.POST.get('new_specialization', '').strip()
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'admin/add_doctor.html', {'specializations': specializations})
        spec = None
        if spec_new:
            spec, _ = Specialization.objects.get_or_create(name=spec_new)
        elif spec_id:
            spec = Specialization.objects.filter(id=spec_id).first()
        user = User.objects.create_user(username=username, email=email, password=password,
                                        first_name=first_name, last_name=last_name)
        UserProfile.objects.create(user=user, role='doctor', phone=phone, address=address)
        Doctor.objects.create(user=user, specialization=spec, phone=phone, address=address,
                              experience_years=exp, qualification=qual,
                              available_from=avail_from, available_to=avail_to)
        messages.success(request, f'Doctor {first_name} {last_name} added successfully.')
        return redirect('doctor_list')
    return render(request, 'admin/add_doctor.html', {'specializations': specializations})

@login_required
def edit_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    profile = UserProfile.objects.filter(user=request.user).first()
    is_admin = request.user.is_superuser or (profile and profile.role == 'admin')
    is_self = hasattr(request.user, 'doctor_profile') and request.user.doctor_profile == doctor
    if not (is_admin or is_self):
        messages.error(request, 'Access denied.')
        return redirect('home')
    specializations = Specialization.objects.all()
    if request.method == 'POST':
        doctor.phone = request.POST.get('phone', doctor.phone)
        doctor.address = request.POST.get('address', doctor.address)
        doctor.experience_years = request.POST.get('experience_years', doctor.experience_years)
        doctor.qualification = request.POST.get('qualification', doctor.qualification)
        doctor.available_from = request.POST.get('available_from', doctor.available_from)
        doctor.available_to = request.POST.get('available_to', doctor.available_to)
        spec_id = request.POST.get('specialization')
        if spec_id:
            doctor.specialization = Specialization.objects.filter(id=spec_id).first()
        doctor.save()
        doctor.user.first_name = request.POST.get('first_name', doctor.user.first_name)
        doctor.user.last_name = request.POST.get('last_name', doctor.user.last_name)
        doctor.user.email = request.POST.get('email', doctor.user.email)
        doctor.user.save()
        messages.success(request, 'Doctor updated.')
        return redirect('doctor_list' if is_admin else 'doctor_dashboard')
    return render(request, 'admin/edit_doctor.html', {'doctor': doctor, 'specializations': specializations})

@login_required
def delete_doctor(request, pk):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not (request.user.is_superuser or (profile and profile.role == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('home')
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.user.delete()
        messages.success(request, 'Doctor deleted.')
        return redirect('doctor_list')
    return render(request, 'admin/confirm_delete.html', {'object': doctor, 'type': 'doctor'})

@login_required
def add_prescription(request, appointment_id=None):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    appointment = None
    patient = None
    if appointment_id:
        appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=doctor)
        patient = appointment.patient
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id') or (patient.id if patient else None)
        appt_id = request.POST.get('appointment_id') or (appointment.id if appointment else None)
        if not patient_id:
            messages.error(request, 'Patient is required.')
            return redirect('doctor_dashboard')
        pat = get_object_or_404(Patient, pk=patient_id)
        appt = Appointment.objects.filter(pk=appt_id).first() if appt_id else None
        Prescription.objects.create(
            doctor=doctor, patient=pat, appointment=appt,
            diagnosis=request.POST.get('diagnosis',''),
            medicines=request.POST.get('medicines',''),
            instructions=request.POST.get('instructions',''),
        )
        if appt:
            appt.status = 'completed'
            appt.save()
        messages.success(request, 'Prescription saved.')
        return redirect('doctor_dashboard')
    patients = Patient.objects.select_related('user').all()
    return render(request, 'doctor/add_prescription.html', {
        'doctor': doctor,
        'appointment': appointment,
        'patient': patient,
        'patients': patients,
    })

@login_required
def prescription_list(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        prescriptions = Prescription.objects.filter(doctor=doctor).select_related('patient__user').order_by('-created_at')
    except Doctor.DoesNotExist:
        # Could be admin or patient
        profile = UserProfile.objects.filter(user=request.user).first()
        if profile and profile.role == 'admin' or request.user.is_superuser:
            prescriptions = Prescription.objects.select_related('patient__user','doctor__user').order_by('-created_at')
        elif hasattr(request.user, 'patient_profile'):
            prescriptions = Prescription.objects.filter(patient=request.user.patient_profile).select_related('doctor__user').order_by('-created_at')
        else:
            prescriptions = Prescription.objects.none()
    return render(request, 'prescriptions.html', {'prescriptions': prescriptions})
