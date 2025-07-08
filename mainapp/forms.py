from django import forms
from .models import Appointment, Doctor
from django.utils import timezone
from django.core.exceptions import ValidationError

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient_name', 'phone_number', 'doctor', 'appointment_date', 'appointment_time', 'notes']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom label for doctor dropdown
        self.fields['doctor'].queryset = Doctor.objects.all()
        self.fields['doctor'].label_from_instance = lambda obj: f"{obj.name} ({obj.specialization})"
        # Set min date in HTML
        self.fields['appointment_date'].widget.attrs['min'] = timezone.now().date().isoformat()

    def clean_patient_name(self):
        name = self.cleaned_data.get('patient_name')
        if not name.replace(' ', '').isalpha():
            raise ValidationError("Enter a valid name (letters and spaces only).")
        return name

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit() or len(phone) != 12:
            raise ValidationError("Phone number must be exactly 12 digits.")
        return phone

    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date and date < timezone.now().date():
            raise ValidationError("Appointment date cannot be in the past.")
        return date
