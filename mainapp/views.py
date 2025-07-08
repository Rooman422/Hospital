from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .forms import AppointmentForm
from .models import Appointment, Treatment, Doctor
from datetime import date  # ✅ Missing import added


def index(request):
    form = AppointmentForm() 
    doctors = Doctor.objects.all().select_related('department')
    return render(request, 'index.html', {
        'doctors': doctors,
        'form': form
    })

def login_view(request):
    """Handle user authentication"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, 'Welcome back!')
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)

        messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'auth.html', {'auth_type': 'login'})


def signup_view(request):
    """Handle new user registration"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

            if not all([username, email, password]):
                raise ValidationError("All fields are required")

            if User.objects.filter(username=username).exists():
                raise ValidationError("Username already exists")

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('index')

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')

    return render(request, 'auth.html', {'auth_type': 'signup'})


def logout_view(request):
    """Handle user logout"""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('index')


@login_required(login_url='login')
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)

        if form.is_valid():
            try:
                appointment = form.save(commit=False)
                appointment.user = request.user
                appointment.save()

                # Store appointment ID in session for success page
                request.session['appointment_id'] = appointment.id

                messages.success(
                    request,
                    f"Appointment with Dr. {appointment.doctor.name} booked successfully!"
                )
                return redirect('appointment_success')

            except Exception as e:
                messages.error(request, f"Could not save appointment: {str(e)}")
        else:
            # Add form errors as messages
            for field, errors in form.errors.items():
                field_name = form.fields[field].label or field.replace('_', ' ').title()
                for error in errors:
                    messages.error(request, f"{field_name}: {error}")

        # Return to index.html with form + doctors
        doctors = Doctor.objects.all()
        return render(request, 'index.html', {
            'form': form,
            'doctors': doctors,
            'min_date': date.today().strftime('%Y-%m-%d')
        })

    return redirect('index')





@login_required
def appointment_success(request):
    appointment_id = request.session.get('appointment_id')

    if not appointment_id:
        messages.warning(request, "No recent appointment to show.")
        return redirect('index')

    appointment = None
    try:
        appointment = Appointment.objects.select_related('doctor').get(id=appointment_id)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")
        return redirect('index')

    return render(request, 'success.html', {'appointment': appointment})


def treatment_list(request):
    treatments = Treatment.objects.all()  # ✅ Remove prefetch_related('doctors')
    return render(request, 'treatments.html', {'treatments': treatments})


@login_required
def search_appointment(request):
    """Search user's own appointments"""
    appointments = Appointment.objects.filter(
        user=request.user
    ).select_related('doctor').order_by('appointment_date')

    return render(request, 'search_appointment.html', {
        'appointments': appointments
    })
