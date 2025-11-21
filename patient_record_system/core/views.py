from django.shortcuts import render
from patients.models import Patient, RecordGroup, PatientFile

def home(request):
    patient = None
    groups = []
    records = []
    query = request.GET.get("q")
    group_filter = request.GET.get("group")

    if request.user.is_authenticated:
        patient = Patient.objects.filter(user=request.user).first()
        if patient:
            groups = patient.groups.all()
            # ✅ FIX: use patient.files instead of patient.records
            records = patient.files.select_related("group").order_by("-uploaded_at")

            # Optional search and filter
            if query:
                records = records.filter(title__icontains=query)
            if group_filter:
                records = records.filter(group__id=group_filter)

    context = {
        "patient": patient,
        "groups": groups,
        "records": records,
        "query": query or "",
        "group_filter": int(group_filter) if group_filter else None,
    }

    return render(request, "core/home.html", context)
