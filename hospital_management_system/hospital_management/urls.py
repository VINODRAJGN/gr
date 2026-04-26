from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from common import views as cv
from patients import views as pv
from doctors import views as dv
from appointments import views as av

urlpatterns = [
    path('admin/', admin.site.urls),
    # Common
    path('', cv.home, name='home'),
    path('register/', cv.register_view, name='register'),
    path('login/', cv.login_view, name='login'),
    path('logout/', cv.logout_view, name='logout'),
    # Dashboards
    path('dashboard/admin/', cv.admin_dashboard, name='admin_dashboard'),
    path('dashboard/doctor/', cv.doctor_dashboard, name='doctor_dashboard'),
    path('dashboard/patient/', cv.patient_dashboard, name='patient_dashboard'),
    path('dashboard/manager/', cv.appointment_manager_dashboard, name='appointment_manager_dashboard'),
    # Patients (admin)
    path('patients/', pv.patient_list, name='patient_list'),
    path('patients/add/', pv.add_patient, name='add_patient'),
    path('patients/<int:pk>/edit/', pv.edit_patient, name='edit_patient'),
    path('patients/<int:pk>/delete/', pv.delete_patient, name='delete_patient'),
    path('profile/', pv.my_profile, name='my_profile'),
    # Doctors (admin)
    path('doctors/', dv.doctor_list, name='doctor_list'),
    path('doctors/add/', dv.add_doctor, name='add_doctor'),
    path('doctors/<int:pk>/edit/', dv.edit_doctor, name='edit_doctor'),
    path('doctors/<int:pk>/delete/', dv.delete_doctor, name='delete_doctor'),
    # Prescriptions
    path('prescriptions/', dv.prescription_list, name='prescription_list'),
    path('prescriptions/add/', dv.add_prescription, name='add_prescription'),
    path('prescriptions/add/<int:appointment_id>/', dv.add_prescription, name='add_prescription_for_appt'),
    # Appointments
    path('appointments/', av.appointment_list, name='appointment_list'),
    path('appointments/book/', av.book_appointment, name='book_appointment'),
    path('appointments/schedule/', av.schedule_appointment, name='schedule_appointment'),
    path('appointments/queue/', av.appointment_queue, name='appointment_queue'),
    path('appointments/<int:pk>/', av.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/status/', av.update_appointment_status, name='update_appointment_status'),
    path('appointments/<int:pk>/cancel/', av.cancel_appointment, name='cancel_appointment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
