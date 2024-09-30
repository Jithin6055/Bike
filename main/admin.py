from django.contrib import admin
from .models import Bike, Rental, Location

admin.site.register(Rental)
admin.site.register(Bike)
admin.site.register(Location)
