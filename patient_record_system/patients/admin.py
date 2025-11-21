from django.contrib import admin
from .models import Patient, PatientFile

admin.site.register(Patient)
admin.site.register(PatientFile)
