import json
import re
import hashlib
import secrets
import os

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.crypto import salted_hmac
from django.contrib.auth.forms import AuthenticationForm

from patients.models import Patient
from .forms import (
    AadhaarRequestOTPForm,
    AadhaarVerifyOTPForm,
)
from .aadhaar_provider import provider  # mock or real provider

# ============================================================
# Load Aadhaar Dummy Data (external JSON)
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AADHAAR_DATA_PATH = os.path.join(os.path.dirname(__file__), "aadhaar_data.json")


if os.path.exists(AADHAAR_DATA_PATH):
    with open(AADHAAR_DATA_PATH, "r") as f:
        AADHAAR_DB = json.load(f)
else:
    AADHAAR_DB = {}


# ============================================================
# Utility Functions
# ============================================================

def make_remember_token():
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def hash_token(token):
    """Return a consistent hash for storing in DB (never store raw token)."""
    return salted_hmac("aadhaar_token", token).hexdigest()


# ============================================================
# Aadhaar OTP–based authentication
# ============================================================

def aadhaar_request_otp(request):
    """Step 1: User enters Aadhaar number → provider sends OTP"""
    if request.method == "POST":
        form = AadhaarRequestOTPForm(request.POST)
        if form.is_valid():
            aadhaar_number = form.cleaned_data["aadhaar_number"].strip()

            # Validate if Aadhaar exists in our local JSON DB
            aadhaar_info = AADHAAR_DB.get(aadhaar_number)
            if not aadhaar_info:
                messages.error(request, "Aadhaar not found in demo database.")
                return render(request, "accounts/request_otp.html", {"form": form})

            try:
                resp = provider.request_otp(aadhaar_number)
                if resp.get("status") == "OK":
                    txn_id = resp["txnId"]
                    verify_form = AadhaarVerifyOTPForm(
                        initial={"aadhaar_number": aadhaar_number, "txnId": txn_id}
                    )
                    debug_otp = resp.get("debug_otp")  # only for dev
                    return render(
                        request,
                        "accounts/verify_otp.html",
                        {"form": verify_form, "debug_otp": debug_otp},
                    )
                else:
                    messages.error(
                        request, f"Failed to request OTP: {resp.get('message', '')}"
                    )
            except Exception as e:
                messages.error(request, f"Error contacting OTP provider: {e}")
    else:
        form = AadhaarRequestOTPForm()
    return render(request, "accounts/request_otp.html", {"form": form})


def aadhaar_verify_otp(request):
    """Step 2: User submits OTP → verify and log in"""
    if request.method == "POST":
        form = AadhaarVerifyOTPForm(request.POST)
        if form.is_valid():
            aadhaar_number = form.cleaned_data["aadhaar_number"]
            txn_id = form.cleaned_data["txnId"]
            otp = form.cleaned_data["otp"]

            resp = provider.verify_otp(aadhaar_number, txn_id, otp)
            if resp.get("status") == "OK":
                # Fetch user info from JSON DB
                info = AADHAAR_DB.get(aadhaar_number, {})
                name = info.get("name", f"user_{aadhaar_number[-4:]}")
                dob = info.get("dob", "1990-01-01")
                masked = f"xxxx-xxxx-{aadhaar_number[-4:]}"

                # Create or get user
                username = f"aad_{aadhaar_number[-6:]}_{hashlib.sha1(aadhaar_number.encode()).hexdigest()[:6]}"
                user, _ = User.objects.get_or_create(
                    username=username, defaults={"first_name": name}
                )

                # Create or get patient record
                aadhaar_hash = hashlib.sha256(aadhaar_number.encode()).hexdigest()
                patient, _ = Patient.objects.get_or_create(
                    user=user,
                    defaults={
                        "name": name,
                        "dob": dob,
                        "masked_aadhaar": masked,
                        "aadhaar_hash": aadhaar_hash,
                    },
                )

                # Update missing details if any
                updated = False
                if not patient.aadhaar_hash:
                    patient.aadhaar_hash = aadhaar_hash
                    updated = True
                if not patient.name:
                    patient.name = name
                    updated = True
                if not patient.dob:
                    patient.dob = dob
                    updated = True
                if updated:
                    patient.save()

                # Generate secure token and set cookie
                token = make_remember_token()
                patient.aadhaar_token = hash_token(token)
                patient.save()

                login(request, user)
                response = redirect("home")
                response.set_cookie(
                    "remember_token",
                    token,
                    max_age=30 * 24 * 3600,  # 30 days
                    secure=True,             # Use HTTPS in production
                    httponly=True,
                    samesite="Lax",
                )
                return response
            else:
                messages.error(
                    request,
                    f"OTP verification failed: {resp.get('message', 'Unknown error')}",
                )

    return redirect("accounts:aadhaar_request_otp")


# ============================================================
# QR-based Aadhaar login
# ============================================================

def qr_login_page(request):
    """Render QR scanner page"""
    return render(request, "accounts/qr_login.html")


def qr_verify(request):
    """Receive scanned QR → verify → login"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST required"}, status=400)

    try:
        body = json.loads(request.body.decode())
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    qr_text = body.get("qr")
    if not qr_text:
        return JsonResponse({"status": "error", "message": "Empty QR"}, status=400)

    # Simulate Aadhaar QR decode
    m = re.search(r"(\d{12})", qr_text.strip())
    aadhaar_number = m.group(1) if m else "000000000000"
    info = AADHAAR_DB.get(aadhaar_number, {})
    name = info.get("name", "QR User")
    dob = info.get("dob", "1990-01-01")
    aadhaar_hash = hashlib.sha256(aadhaar_number.encode()).hexdigest()

    username = f"qr_{aadhaar_hash[:8]}"
    user, _ = User.objects.get_or_create(username=username, defaults={"first_name": name})
    patient, _ = Patient.objects.get_or_create(
        user=user,
        defaults={"name": name, "dob": dob, "aadhaar_hash": aadhaar_hash},
    )

    # Generate secure token and cookie
    token = make_remember_token()
    patient.aadhaar_token = hash_token(token)
    patient.save()

    login(request, user)
    response = JsonResponse({"status": "ok", "redirect": "/"})
    response.set_cookie(
        "remember_token",
        token,
        max_age=30 * 24 * 3600,
        secure=True,
        httponly=True,
        samesite="Lax",
    )
    return response


# ============================================================
# Admin Login (optional)
# ============================================================

def login_view(request):
    """Basic Django admin/test login"""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


# ============================================================
# Logout
# ============================================================

def logout_view(request):
    """Logout and clear cookies"""
    response = redirect("home")
    response.delete_cookie("remember_token")
    logout(request)
    return response
