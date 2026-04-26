from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Appointment
from patients.models import Patient
from doctors.models import Doctor
from common.models import UserProfile
from datetime import date, datetime, timedelta

@login_required
def book_appointment(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Only patients can book appointments.')
        return redirect('home')
    doctors = Doctor.objects.filter(is_active=True).select_related('user','specialization')
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        appt_date = request.POST.get('appointment_date')
        appt_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason', '')
        priority = request.POST.get('priority', 'normal')
        if not doctor_id or not appt_date or not appt_time:
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'patient/book_appointment.html', {'doctors': doctors})
        doctor = get_object_or_404(Doctor, pk=doctor_id)
        # Check if already booked
        if Appointment.objects.filter(doctor=doctor, appointment_date=appt_date, appointment_time=appt_time, status__in=['pending','confirmed']).exists():
            messages.error(request, 'This time slot is already booked. Please choose another.')
            return render(request, 'patient/book_appointment.html', {'doctors': doctors})
        # Assign queue number for same day
        same_day_count = Appointment.objects.filter(doctor=doctor, appointment_date=appt_date).count()
        appt = Appointment.objects.create(
            patient=patient, doctor=doctor,
            appointment_date=appt_date, appointment_time=appt_time,
            reason=reason, priority=priority,
            queue_number=same_day_count + 1
        )
        messages.success(request, f'Appointment booked! Queue number: {appt.queue_number}')
        return redirect('patient_dashboard')
    return render(request, 'patient/book_appointment.html', {'doctors': doctors})

@login_required
def appointment_list(request):
    """Admin/Manager view all appointments"""
    profile = UserProfile.objects.filter(user=request.user).first()
    if not (request.user.is_superuser or (profile and profile.role in ['admin','appointment_manager'])):
        messages.error(request, 'Access denied.')
        return redirect('home')
    appointments = Appointment.objects.select_related(
        'patient__user','doctor__user','doctor__specialization'
    ).order_by('-appointment_date','-appointment_time')
    status_filter = request.GET.get('status','')
    date_filter = request.GET.get('date','')
    doctor_filter = request.GET.get('doctor','')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
    if doctor_filter:
        appointments = appointments.filter(doctor_id=doctor_filter)
    doctors = Doctor.objects.select_related('user').all()
    return render(request, 'manager/appointments.html', {
        'appointments': appointments,
        'doctors': doctors,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'status_choices': Appointment.STATUS_CHOICES,
    })

@login_required
def update_appointment_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    profile = UserProfile.objects.filter(user=request.user).first()
    is_admin = request.user.is_superuser or (profile and profile.role in ['admin','appointment_manager'])
    is_doctor = hasattr(request.user, 'doctor_profile') and request.user.doctor_profile == appt.doctor
    if not (is_admin or is_doctor):
        messages.error(request, 'Access denied.')
        return redirect('home')
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        if new_status in dict(Appointment.STATUS_CHOICES):
            appt.status = new_status
            if notes:
                appt.notes = notes
            appt.save()
            messages.success(request, f'Appointment status updated to {new_status}.')
    return redirect(request.META.get('HTTP_REFERER', 'appointment_list'))

@login_required
def cancel_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    is_patient = hasattr(request.user, 'patient_profile') and request.user.patient_profile == appt.patient
    profile = UserProfile.objects.filter(user=request.user).first()
    is_admin = request.user.is_superuser or (profile and profile.role in ['admin','appointment_manager'])
    if not (is_patient or is_admin):
        messages.error(request, 'Access denied.')
        return redirect('home')
    appt.status = 'cancelled'
    appt.save()
    messages.success(request, 'Appointment cancelled.')
    return redirect('patient_dashboard' if is_patient else 'appointment_list')

@login_required
def schedule_appointment(request):
    """Appointment manager scheduling view"""
    profile = UserProfile.objects.filter(user=request.user).first()
    if not (request.user.is_superuser or (profile and profile.role in ['admin','appointment_manager'])):
        messages.error(request, 'Access denied.')
        return redirect('home')
    doctors = Doctor.objects.filter(is_active=True).select_related('user','specialization')
    patients = Patient.objects.select_related('user').all()
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        appt_date = request.POST.get('appointment_date')
        appt_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason','')
        priority = request.POST.get('priority','normal')
        doctor = get_object_or_404(Doctor, pk=doctor_id)
        patient = get_object_or_404(Patient, pk=patient_id)
        same_day_count = Appointment.objects.filter(doctor=doctor, appointment_date=appt_date).count()
        Appointment.objects.create(
            patient=patient, doctor=doctor,
            appointment_date=appt_date, appointment_time=appt_time,
            reason=reason, priority=priority, status='confirmed',
            queue_number=same_day_count + 1
        )
        messages.success(request, 'Appointment scheduled.')
        return redirect('appointment_list')
    return render(request, 'manager/schedule.html', {'doctors': doctors, 'patients': patients,
        'priority_choices': Appointment.PRIORITY_CHOICES})

@login_required
def appointment_queue(request):
    """Show today's queue"""
    today = date.today()
    doctor_filter = request.GET.get('doctor','')
    appointments = Appointment.objects.filter(
        appointment_date=today, status__in=['pending','confirmed']
    ).select_related('patient__user','doctor__user').order_by('priority','appointment_time')
    if doctor_filter:
        appointments = appointments.filter(doctor_id=doctor_filter)
    doctors = Doctor.objects.filter(is_active=True).select_related('user')
    # Check late notifications
    late_notifications = []
    now = datetime.now()
    for appt in appointments:
        appt_dt = datetime.combine(appt.appointment_date, appt.appointment_time)
        if now > appt_dt - timedelta(minutes=30) and not appt.notification_sent:
            late_notifications.append(appt)
            appt.notification_sent = True
            appt.save()
    return render(request, 'manager/queue.html', {
        'appointments': appointments,
        'doctors': doctors,
        'late_notifications': late_notifications,
        'today': today,
    })

@login_required
def appointment_detail(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointment_detail.html', {'appointment': appt})
