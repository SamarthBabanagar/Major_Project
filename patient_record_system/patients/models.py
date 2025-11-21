from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


# ---------- Helper Function ----------
def patient_file_upload_to(instance, filename):
    """Store files under /media/patient_files/<patient_id>/timestamp_filename"""
    timestamp = int(timezone.now().timestamp())
    return f'patient_files/{instance.patient.id}/{timestamp}_{filename}'


# ---------- Core Models ----------
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    dob = models.DateField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    aadhaar_hash = models.CharField(max_length=128, blank=True, null=True, unique=True)
    masked_aadhaar = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class RecordGroup(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PatientFile(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='files')
    group = models.ForeignKey(RecordGroup, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=patient_file_upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or os.path.basename(self.file.name)

    def delete(self, *args, **kwargs):
        """
        Ensure the physical file is deleted from /media when record is deleted.
        """
        try:
            if self.file and os.path.isfile(self.file.path):
                os.remove(self.file.path)
        except Exception:
            pass

        super().delete(*args, **kwargs)
