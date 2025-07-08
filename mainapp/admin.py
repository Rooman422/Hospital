from django.contrib import admin
from .models import Appointment, Doctor, Department, Treatment, UserProfile


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'department')
    list_filter = ('department', 'specialization')
    search_fields = ('name', 'specialization')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date', 'doctor')
    search_fields = ('patient_name', 'doctor__name')
    date_hierarchy = 'appointment_date'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone') 
    search_fields = ('user__username', 'phone_number')


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'price', 'duration', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_active')
    fieldsets = (
        (None, {
            'fields': ('name', 'department')
        }),
        ('Details', {
            'fields': ('description', 'price', 'duration')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
