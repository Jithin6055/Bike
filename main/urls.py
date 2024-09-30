from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('bikes/', views.bike_list, name='bike_list'),  # List all available bikes
    path('bike/<int:bike_id>/', views.bike_detail, name='bike_detail'),  # Detail page for each bike
    path('rent/<int:bike_id>/', views.rent_bike, name='rent_bike'),  # Form to rent a bike
    path('my-bookings/', views.my_bookings, name='my_bookings'),  # List user's bookings
    path('booking-confirmation/<int:rental_id>/', views.booking_confirmation, name='booking_confirmation'),  # Confirmation page
    path('login/', views.login_view, name='login'),  # User login
    path('logout/', views.logout_view, name='logout'),  # User logout
    path('signup/', views.signup_view, name='signup'),  # User signup

    path('cancel_rental/<int:rental_id>/', views.cancel_rental, name='cancel_rental'),
    path('compare/', views.bike_comparison, name='bike_comparison'),
]
