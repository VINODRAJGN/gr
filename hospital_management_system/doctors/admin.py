from django.contrib import admin
from .models import Doctor, Specialization, Prescription
admin.site.register(Specialization)
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'specialization', 'phone', 'experience_years', 'is_active']
    def get_name(self, obj): return f"Dr. {obj.user.get_full_name()}"
    get_name.short_description = 'Name'
admin.site.register(Prescription)
