from django.shortcuts import render, get_object_or_404, redirect
from .models import Bike, Rental, Location
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .ai_generator import generate_bike_comparison
from django.db.models import Count

# Home page view
def home(request):
    print(now())
    return render(request, 'main/home.html')


# List all available bikes
def bike_list(request):
    bikes = Bike.objects.filter(available=True)  # Only show available bikes
    return render(request, 'main/bike_list.html', {'bikes': bikes})


# Display bike details
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Bike
from django.shortcuts import render, get_object_or_404, redirect
from .models import Bike # Ensure this is imported
from django.contrib import messages

def bike_detail(request, bike_id):
    bike = get_object_or_404(Bike, id=bike_id)

    # Handle bike comparison
    if request.method == 'POST':
        bike1_id = bike_id  # The bike being viewed
        bike2_id = request.POST.get('bike2')

        if bike2_id == str(bike1_id):
            messages.info(request, 'Choose a different bike for comparison!')
            return redirect('bike_detail', bike_id=bike1_id)

        # Fetch the second bike details
        bike2 = Bike.objects.get(id=bike2_id)

        # Prepare bike details for the AI function
        bike1_details = {
            'brand': bike.brand,
            'model': bike.model,
            'mileage': bike.mileage,
            'price_per_hour': bike.price_per_hour,
        }

        bike2_details = {
            'brand': bike2.brand,
            'model': bike2.model,
            'mileage': bike2.mileage,
            'price_per_hour': bike2.price_per_hour,
        }

        # Generate the comparison response
        comparison_text = generate_bike_comparison(bike1_details, bike2_details)

        # Determine the best bike based on mileage (or any other criteria)
        best_bike = bike if bike.mileage > bike2.mileage else bike2

        return render(request, 'main/bike_comparison.html', {
            'bike1': bike,
            'bike2': bike2,
            'comparison_text': comparison_text,
            'best_bike': best_bike
        })

    bikes = Bike.objects.all()  # Fetch all bikes for comparison
    return render(request, 'main/bike_detail.html', {'bike': bike, 'bikes': bikes})



# Rent a bike (rental form manually handled in HTML)
@login_required
def rent_bike(request, bike_id):
    bike = get_object_or_404(Bike, id=bike_id)
    
    if request.method == 'POST':
        # Access form values using their 'id' from the HTML form
        pickup_location_id = request.POST.get('pickup_location_id')
        dropoff_location_id = request.POST.get('dropoff_location_id')
        pickup_date_str = request.POST.get('pickup_date')
        dropoff_date_str = request.POST.get('dropoff_date')

        print(f'Pickup Date: {pickup_date_str}, Dropoff Date: {dropoff_date_str}')
        
        # Convert dates from strings to datetime objects
        try:
            pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%dT%H:%M')  # Adjust format here
            dropoff_date = datetime.strptime(dropoff_date_str, '%Y-%m-%dT%H:%M')  # Adjust format here
        except ValueError:
            messages.error(request, 'Invalid date format. Please select the date and time correctly.')
            return redirect('rent_bike', bike_id=bike.id)
        
        # Fetch locations from the database
        pickup_location = get_object_or_404(Location, id=pickup_location_id)
        dropoff_location = get_object_or_404(Location, id=dropoff_location_id)
        
        # Calculate rental duration and price
        rental = Rental(
            user=request.user,
            bike=bike,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            pickup_date=pickup_date,
            dropoff_date=dropoff_date
        )
        rental.total_price = rental.calculate_total_price()
        rental.save()
        
        messages.success(request, 'Bike rental successful! Enjoy your ride.')
        return redirect('booking_confirmation', rental_id=rental.id)
    
    # Pass locations to template for the form
    locations = Location.objects.all()
    return render(request, 'main/bike_rent.html', {'bike': bike, 'locations': locations})


# Show user's bookings
@login_required
def my_bookings(request):
    rentals = Rental.objects.filter(user=request.user)
    return render(request, 'main/my_bookings.html', {'bookings': rentals, 'now': now()})


# Booking confirmation page
@login_required
def booking_confirmation(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)
    messages.info(request, 'REMINDER: If your rental is overdue, additional charges will be applied!')
    return render(request, 'main/booking_confirmation.html', {'booking': rental})


# User login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful! Welcome back.')
            
            # Check if the user is staff (admin)
            if user.is_staff:
                return redirect('rental_visualization')  # Redirect to rental visualization for admin
            else:
                return redirect('home')  # Redirect to home for regular users
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'main/login.html')


# User logout view
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')
    return redirect('home')


from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Username validation: Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose a different one.')
            return redirect('signup')

        # Password validation
        if password != confirm_password:
            messages.error(request, 'Passwords do not match. Please try again.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        elif not any(char.isdigit() for char in password):
            messages.error(request, 'Password must contain at least one numeral.')
        elif not any(char.isalpha() for char in password):
            messages.error(request, 'Password must contain at least one letter.')
        elif not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in password):
            messages.error(request, 'Password must contain at least one special character.')
        else:
            try:
                # Create user
                user = User.objects.create_user(username=username, password=password)
                # Log in the user
                login(request, user)
                messages.success(request, 'Signup successful! Welcome to WheelStreet.')
                return redirect('home')
            except ValidationError:
                messages.error(request, 'Invalid username. Please choose a different one.')
            except Exception as e:
                # Catch any other errors (like database-related issues)
                messages.error(request, f'An error occurred: {str(e)}')
                return redirect('signup')

    return render(request, 'main/signup.html')


# Cancel rental
@login_required
def cancel_rental(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)  # Ensure only the user can cancel their own rental

    # Cancel the rental
    rental.delete()
    messages.success(request, 'Your booking has been canceled successfully.')
    
    return redirect('my_bookings')


def bike_comparison(request):
    if request.method == 'POST':
        # Get selected bike IDs from the form
        bike1_id = request.POST.get('bike1')
        bike2_id = request.POST.get('bike2')

        if bike1_id == bike2_id:
            messages.info(request, 'Choose different bikes for comparison!')
            return redirect('bike_comparison')

        # Fetch bike details from the database
        bike1 = Bike.objects.get(id=bike1_id)
        bike2 = Bike.objects.get(id=bike2_id)

        # Prepare bike details for the AI function
        bike1_details = {
            'brand': bike1.brand,
            'model': bike1.model,
            'mileage': bike1.mileage,
            'price_per_hour': bike1.price_per_hour,  # Corrected to use bike1
        }

        bike2_details = {
            'brand': bike2.brand,
            'model': bike2.model,
            'mileage': bike2.mileage,
            'price_per_hour': bike2.price_per_hour,
        }

        # Generate the comparison response
        comparison_text = generate_bike_comparison(bike1_details, bike2_details)

        # Determine the best bike based on mileage (or any other criteria)
        best_bike = bike1 if bike1.mileage > bike2.mileage else bike2

        return render(request, 'main/bike_comparison.html', {
            'bike1': bike1,
            'bike2': bike2,
            'comparison_text': comparison_text,
            'best_bike': best_bike  # Pass the best bike to the template
        })

    # If not a POST request, display the comparison form
    bikes = Bike.objects.all()
    return render(request, 'main/bike_comparison_form.html', {'bikes': bikes})


def combined_rental_visualization(request):
    # Pie chart data (bike types)
    bike_rental_data = (
        Rental.objects.values('bike__bike_type')
        .annotate(rental_count=Count('bike'))
        .order_by('-rental_count')
    )
    
    bike_types = [Bike.BIKE_TYPES_DICT[rental['bike__bike_type']] for rental in bike_rental_data]
    rental_counts_by_type = [rental['rental_count'] for rental in bike_rental_data]

    # Bar chart data (most rented bikes)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    rental_queryset = Rental.objects.all()

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        rental_queryset = rental_queryset.filter(pickup_date__gte=start_date, dropoff_date__lte=end_date)

    most_rented_bikes = (
        rental_queryset.values('bike__model')
        .annotate(rental_count=Count('bike'))
        .order_by('-rental_count')
    )

    bike_models = [rental['bike__model'] for rental in most_rented_bikes]
    rental_counts_by_model = [rental['rental_count'] for rental in most_rented_bikes]

    context = {
        'bike_types': bike_types,
        'rental_counts': rental_counts_by_type,
        'bike_models': bike_models,
        'rental_counts_by_model': rental_counts_by_model,
        'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else '',
    }

    return render(request, 'main/combined_rental_visualization.html', context)

from django.db.models import Sum, Count
def sales_report_view(request):
    # Get total sales and number of rentals
    total_sales = Rental.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_rentals = Rental.objects.aggregate(Count('id'))['id__count'] or 0

    # Optional: Breakdown by bike type
    sales_by_bike_type = Rental.objects.values('bike__bike_type').annotate(
        total_sales=Sum('total_price'),
        count=Count('id')
    )

    # Logging the values for debugging
    print(f'Total Sales: {total_sales}, Total Rentals: {total_rentals}')

    context = {
        'total_sales': total_sales,
        'total_rentals': total_rentals,
        'sales_by_bike_type': sales_by_bike_type,
    }
    return render(request, 'main/sales_report.html', context)