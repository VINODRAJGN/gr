from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Patient
from common.models import UserProfile
from appointments.models import Appointment
from doctors.models import Doctor, Prescription

@login_required
def patient_list(request):
    """Admin only - list all patients"""
    profile = UserProfile.objects.filter(user=request.user).first()
    if not (request.user.is_superuser or (profile and profile.role == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('home')
    patients = Patient.objects.select_related('user').order_by('-created_at')
    return render(request, 'admin/patients.html', {'patients': patients})

@login_required
def add_patient(request):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not (request.user.is_superuser or (profile and profile.role == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('home')
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password', 'patient123')
        age = request.POST.get('age', 0)
        gender = request.POST.get('gender', 'Male')
        blood_group = request.POST.get('blood_group', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'admin/add_patient.html')
        user = User.objects.create_user(username=username, email=email, password=password,
                                        first_name=first_name, last_name=last_name)
        UserProfile.objects.create(user=user, role='patient', phone=phone, address=address)
        Patient.objects.create(user=user, age=age, gender=gender, blood_group=blood_group,
                               phone=phone, address=address)
        messages.success(request, 'Patient added successfully.')
        return redirect('patient_list')
    return render(request, 'admin/add_patient.html')

@login_required
def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    profile = UserProfile.objects.filter(user=request.user).first()
    is_admin = request.user.is_superuser or (profile and profile.role == 'admin')
    is_self = hasattr(request.user, 'patient_profile') and request.user.patient_profile == patient
    if not (is_admin or is_self):
        messages.error(request, 'Access denied.')
        return redirect('home')
    if request.method == 'POST':
        patient.age = request.POST.get('age', patient.age)
        patient.gender = request.POST.get('gender', patient.gender)
        patient.blood_group = request.POST.get('blood_group', patient.blood_group)
        patient.phone = request.POST.get('phone', patient.phone)
        patient.address = request.POST.get('address', patient.address)
        patient.emergency_contact = request.POST.get('emergency_contact', patient.emergency_contact)
        patient.save()
        patient.user.first_name = request.POST.get('first_name', patient.user.first_name)
        patient.user.last_name = request.POST.get('last_name', patient.user.last_name)
        patient.user.email = request.POST.get('email', patient.user.email)
        patient.user.save()
        messages.success(request, 'Patient updated successfully.')
        return redirect('patient_list' if is_admin else 'patient_dashboard')
    return render(request, 'admin/edit_patient.html', {'patient': patient})

@login_required
def delete_patient(request, pk):
    profile = UserProfile.objects.filter(user=request.user).first()
    if not (request.user.is_superuser or (profile and profile.role == 'admin')):
        messages.error(request, 'Access denied.')
        return redirect('home')
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.user.delete()
        messages.success(request, 'Patient deleted.')
        return redirect('patient_list')
    return render(request, 'admin/confirm_delete.html', {'object': patient, 'type': 'patient'})

@login_required
def my_profile(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('home')
    return render(request, 'patient/profile.html', {'patient': patient})
