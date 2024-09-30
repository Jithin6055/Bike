from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

# Location model
class Location(models.Model):
    name = models.CharField(max_length=255)  # Name of the location
    address = models.TextField()  # Address of the location
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

# Bike model
class Bike(models.Model):
    BIKE_TYPES = [
        ('Road', 'Road Bike'),
        ('Mountain', 'Mountain Bike'),
        ('Hybrid', 'Hybrid Bike'),
        ('Electric', 'Electric Bike')
    ]
    
    bike_type = models.CharField(max_length=20, choices=BIKE_TYPES)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)  # Pricing for hourly rentals
    available = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    mileage = models.DecimalField(max_digits=6, decimal_places=2)  # Bike mileage in kilometers or miles
    image = models.ImageField(upload_to='bike_images/', blank=True, null=True)  # Image upload path

    def __str__(self):
        return f'{self.brand} {self.model} - {self.bike_type}'

# Rental model
class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)
    pickup_location = models.ForeignKey(Location, related_name='pickups', on_delete=models.CASCADE, null=True)
    dropoff_location = models.ForeignKey(Location, related_name='dropoffs', on_delete=models.CASCADE, null=True)
    pickup_date = models.DateTimeField()
    dropoff_date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_total_price(self):
        hours = (self.dropoff_date - self.pickup_date).total_seconds() / 3600  # Convert to hours
        hours_decimal = Decimal(hours)  # Convert to Decimal
        return self.bike.price_per_hour * hours_decimal
    
    def __str__(self):
        return f'{self.user.username} rented {self.bike} on {self.pickup_date}'
    
