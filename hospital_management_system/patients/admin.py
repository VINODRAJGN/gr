from django.contrib import admin
from .models import Patient
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'age', 'gender', 'blood_group', 'phone']
    def get_name(self, obj): return obj.user.get_full_name()
    get_name.short_description = 'Name'
