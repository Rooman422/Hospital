from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import uuid
from datetime import date

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(help_text="Years of experience")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, validators=[RegexValidator(r'^[0-9]{10,15}$')])
    available_days = models.CharField(max_length=100, default="Monday-Friday")

    # FIXED: Add a default to prevent migration errors
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    patient_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, validators=[RegexValidator(r'^[0-9]{10,15}$')])
    appointment_date = models.DateField()
    appointment_time = models.TimeField(default="09:00")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    # ✅ NEW FIELD
    unique_id = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        ordering = ['-appointment_date', 'appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = f'APT-{date.today().year}-{uuid.uuid4().hex[:6].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_name} with Dr. {self.doctor.name} on {self.appointment_date}"


class Treatment(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the treatment (e.g., Dental Cleaning)")
    description = models.TextField(help_text="Detailed description of the treatment")
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price in local currency"
    )
    duration = models.DurationField(help_text="Estimated treatment duration (HH:MM:SS)")
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='treatments',
        help_text="Department offering this treatment"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this treatment is currently offered")

    class Meta:
        ordering = ['name']
        verbose_name = "Medical Treatment"
        verbose_name_plural = "Medical Treatments"

    def __str__(self):
        return f"{self.name} (${self.price})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^[0-9]{10,15}$')],
        help_text="Optional phone number (10-15 digits)"
    )
    address = models.TextField(blank=True, help_text="User's address (optional)")

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
