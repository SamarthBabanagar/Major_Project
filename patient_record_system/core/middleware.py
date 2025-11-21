from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import login
from patients.models import Patient
from django.utils.crypto import salted_hmac

class AutoLoginMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            return

        token = request.COOKIES.get("remember_token")
        if not token:
            return

        hashed = salted_hmac("aadhaar_token", token).hexdigest()
        try:
            patient = Patient.objects.get(aadhaar_token=hashed)
            login(request, patient.user)
        except Patient.DoesNotExist:
            pass
