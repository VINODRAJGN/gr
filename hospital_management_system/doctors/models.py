from django.db import models
from django.contrib.auth.models import User

class Specialization(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    qualification = models.CharField(max_length=200, blank=True)
    available_from = models.TimeField(default='09:00')
    available_to = models.TimeField(default='17:00')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

class Prescription(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE)
    appointment = models.OneToOneField('appointments.Appointment', on_delete=models.SET_NULL, null=True, blank=True)
    diagnosis = models.TextField()
    medicines = models.TextField()
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient} by {self.doctor}"
