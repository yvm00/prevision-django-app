from django.contrib import admin
from .models import Forecast, Saved

admin.site.register(Forecast)
admin.site.register(Saved)

