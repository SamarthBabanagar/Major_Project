from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Aadhaar OTP-based login
    path('otp/request/', views.aadhaar_request_otp, name='aadhaar_request_otp'),
    path('otp/verify/', views.aadhaar_verify_otp, name='aadhaar_verify_otp'),

    # QR-based login
    path('qr/', views.qr_login_page, name='qr_login'),
    path('qr/verify/', views.qr_verify, name='qr_verify'),

    # Traditional login/signup (optional)
    # path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),

    # Logout
    path('logout/', views.logout_view, name='logout'),
]
