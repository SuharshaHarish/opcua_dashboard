from django.contrib import admin
from .models import Temperature,Pressure,Anomaly

admin.site.register(Temperature)
admin.site.register(Pressure)
admin.site.register(Anomaly)
