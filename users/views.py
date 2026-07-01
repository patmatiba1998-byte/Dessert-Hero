from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomAuthenticationForm
from django.core.mail import send_mail
import random

# View for login
import logging
import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
from .forms import CustomAuthenticationForm

# Set up logging
logger = logging.getLogger(__name__)

def login_view(request):
    # Check if the request method is POST
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)

        # Check if the form is valid
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Log the received credentials for debugging (be careful with logging sensitive info)
            logger.info(f"Attempting to authenticate user: {username}")

            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.email == email:
                # If user is authenticated, log them in
                login(request, user)
                logger.info(f"User {username} authenticated and logged in successfully.")

                # Generate a random verification code
                verification_code = random.randint(100000, 999999)
                request.session['verification_code'] = verification_code

                # Send the verification code to the user's email
                send_mail(
                    'Your Verification Code',
                    f'Your verification code is: {verification_code}',
                    'blessingbraelly@gmail.com',  # Replace with your email address
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f"Verification code sent to {user.email}")

                # Redirect to the verification page
                return redirect('users:verify_code')

            else:
                # If authentication fails, log the error
                logger.error("Invalid credentials or email.")
                messages.error(request, 'Invalid credentials or email.')

        else:
            # If form is not valid, log the error
            logger.error("Form is not valid. Form errors: %s", form.errors)
            messages.error(request, 'Form is not valid. Please check your credentials.')

    else:
        # Handle GET request (when the login form is displayed)
        logger.info("Displaying the login form (GET request).")
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})



# View for code verification
def verify_code_view(request):
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code')

        if entered_code == str(request.session.get('verification_code')):
            user = request.user

            # Logic to check the email and show the modal
            if user.email == 'patmatiba.1998@gmail.com' or user.email == 'kalakoalice45@gmail.com':
                request.session['show_dashboard_modal'] = True
                return render(request, 'verify_code.html', {'show_modal': True})

            else:
                # Redirect to dashboard 1 after verification for any other email
                return redirect('users:dashboard1')

        else:
            messages.error(request, 'Invalid verification code.')

    return render(request, 'verify_code.html', {'show_modal': False})

# Dashboard 1 view
def dashboard1_view(request):
    return render(request, 'dashboard1.html')


# Dashboard 2 view
def dashboard2_view(request):
    return render(request, 'dashboard2.html')
