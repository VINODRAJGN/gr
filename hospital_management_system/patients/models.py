from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.IntegerField(default=0)
    gender = models.CharField(max_length=10, choices=[('Male','Male'),('Female','Female'),('Other','Other')])
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
