from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from io import BytesIO
import zipfile
import os

from .models import Patient, PatientFile, RecordGroup
from .forms import PatientFileUploadForm, BatchUploadForm, RecordGroupForm


# -----------------------------------------
# Upload Options
# -----------------------------------------
@login_required
def upload_choice(request):
    """Render page to choose single or batch upload."""
    return render(request, 'patients/upload_choice.html')


# -----------------------------------------
# Single Upload
# -----------------------------------------
@login_required
def upload_file(request):
    """Handle uploading a single file."""
    patient = get_object_or_404(Patient, user=request.user)

    if request.method == 'POST':
        form = PatientFileUploadForm(patient, request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.patient = patient

            # Handle new or existing group
            new_group_name = form.cleaned_data.get('new_group_name')
            if new_group_name:
                group = RecordGroup.objects.create(patient=patient, name=new_group_name)
                file_obj.group = group
            else:
                group = form.cleaned_data.get('group')
                if group:
                    file_obj.group = group

            # Default title = file name
            if not file_obj.title:
                file_obj.title = file_obj.file.name

            file_obj.save()
            messages.success(request, f"✅ File '{file_obj.title}' uploaded successfully!")
            return redirect('patients:upload_success')
    else:
        form = PatientFileUploadForm(patient)

    return render(request, 'patients/upload_file.html', {'form': form, 'patient': patient})


# -----------------------------------------
# Batch Upload
# -----------------------------------------
@login_required
def batch_upload(request):
    patient = get_object_or_404(Patient, user=request.user)

    if request.method == "POST":
        files = request.FILES.getlist("files")
        form = BatchUploadForm(patient, request.POST)

        if not files:
            messages.error(request, "Please select one or more files to upload.")
            return redirect("patients:batch_upload")

        if form.is_valid():
            title = form.cleaned_data.get("title", "")
            description = form.cleaned_data.get("description", "")
            existing_group = form.cleaned_data.get("group")
            new_group_name = form.cleaned_data.get("new_group_name")

            # Decide group
            group = None
            if new_group_name:
                group, _ = RecordGroup.objects.get_or_create(patient=patient, name=new_group_name.strip())
            elif existing_group:
                group = existing_group

            # Create each file
            for f in files:
                PatientFile.objects.create(
                    patient=patient,
                    group=group,
                    file=f,
                    title=title or f.name,
                    description=description,
                )

            messages.success(request, f"{len(files)} file(s) uploaded successfully!")
            return redirect("patients:upload_success")

        else:
            print("Form errors:", form.errors)
            messages.error(request, "Form invalid — please check inputs.")

    else:
        form = BatchUploadForm(patient)

    return render(request, "patients/batch_upload.html", {"form": form})


# -----------------------------------------
# Ungrouped Files
# -----------------------------------------
@login_required
def ungrouped_files(request):
    patient = get_object_or_404(Patient, user=request.user)
    files = PatientFile.objects.filter(patient=patient, group__isnull=True).order_by('-uploaded_at')
    return render(request, 'patients/ungrouped_files.html', {'files': files})


# -----------------------------------------
# Delete File (Permanent)
# -----------------------------------------
@login_required
def delete_file(request, file_id):
    """Completely delete a file from the system."""
    file_obj = get_object_or_404(PatientFile, id=file_id, patient__user=request.user)

    if request.method == "POST":
        file_title = file_obj.title or file_obj.file.name
        file_obj.delete()
        messages.success(request, f"🗑 File '{file_title}' permanently deleted.")
        return redirect("patients:my_records")

    messages.warning(request, "Invalid request. Please confirm deletion properly.")
    return redirect("patients:my_records")


# -----------------------------------------
# Remove File From Group (Keep file)
# -----------------------------------------
@login_required
def remove_from_group(request, file_id):
    """Remove a file from its group (does NOT delete file)."""
    file_obj = get_object_or_404(PatientFile, id=file_id, patient__user=request.user)

    if request.method == "POST":
        if not file_obj.group:
            messages.info(request, f"ℹ️ File '{file_obj.title}' is not part of any group.")
            return redirect("patients:my_records")

        group_name = file_obj.group.name
        file_obj.group = None
        file_obj.save()
        messages.success(request, f"✅ '{file_obj.title}' removed from group '{group_name}'.")
        return redirect("patients:my_records")

    messages.warning(request, "Invalid request.")
    return redirect("patients:my_records")



# -----------------------------------------
# Upload Success
# -----------------------------------------
@login_required
def upload_success(request):
    return render(request, 'patients/upload_success.html')


# -----------------------------------------
# My Records
# -----------------------------------------
@login_required
def my_records(request):
    patient = get_object_or_404(Patient, user=request.user)
    groups = patient.groups.all()
    files = patient.files.select_related('group').all()
    return render(request, 'patients/my_records.html', {
        'patient': patient,
        'groups': groups,
        'files': files
    })


# -----------------------------------------
# Create Group
# -----------------------------------------
@login_required
def create_group(request):
    patient = get_object_or_404(Patient, user=request.user)
    ungrouped_files = patient.files.filter(group__isnull=True)

    if request.method == 'POST':
        group_name = request.POST.get('name')
        selected_files = request.POST.getlist('existing_files')
        uploaded_files = request.FILES.getlist('new_files')

        if not group_name:
            messages.error(request, "Please enter a group name.")
            return redirect('patients:create_group')

        group = RecordGroup.objects.create(patient=patient, name=group_name)

        # Add existing files
        for fid in selected_files:
            try:
                file = PatientFile.objects.get(id=fid, patient=patient)
                file.group = group
                file.save()
            except PatientFile.DoesNotExist:
                continue

        # Add newly uploaded files
        for f in uploaded_files:
            PatientFile.objects.create(
                patient=patient,
                title=f.name,
                file=f,
                group=group
            )

        messages.success(request, f"✅ Group '{group.name}' created successfully with files!")
        return redirect('patients:my_records')

    return render(request, 'patients/create_group.html', {'ungrouped_files': ungrouped_files})


# -----------------------------------------
# Add to Group
# -----------------------------------------
@login_required
def add_to_group(request, group_id):
    group = get_object_or_404(RecordGroup, id=group_id, patient__user=request.user)
    patient = group.patient
    ungrouped_files = patient.files.filter(group__isnull=True)

    if request.method == 'POST':
        selected_files = request.POST.getlist('existing_files')
        uploaded_files = request.FILES.getlist('new_files')

        for fid in selected_files:
            try:
                f = PatientFile.objects.get(id=fid, patient=patient)
                f.group = group
                f.save()
            except PatientFile.DoesNotExist:
                continue

        for f in uploaded_files:
            PatientFile.objects.create(
                patient=patient,
                title=f.name,
                file=f,
                group=group
            )

        messages.success(request, f"✅ Files added to group '{group.name}'.")
        return redirect('patients:my_records')

    return render(request, 'patients/add_to_group.html', {
        'group': group,
        'ungrouped_files': ungrouped_files
    })


# -----------------------------------------
# Delete Group
# -----------------------------------------
@login_required
def delete_group(request, group_id):
    patient = get_object_or_404(Patient, user=request.user)
    group = get_object_or_404(RecordGroup, id=group_id, patient=patient)
    group.delete()
    messages.success(request, f"✅ Group '{group.name}' deleted successfully!")
    return redirect('patients:my_records')


# -----------------------------------------
# Download Group as ZIP
# -----------------------------------------
@login_required
def download_group(request, group_id):
    group = get_object_or_404(RecordGroup, id=group_id, patient__user=request.user)
    files = group.patient.files.filter(group=group)

    if not files.exists():
        messages.warning(request, "No files found in this group.")
        return redirect('patients:my_records')

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for f in files:
            with f.file.open('rb') as file_data:
                zip_file.writestr(f.file.name.split('/')[-1], file_data.read())

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{group.name}.zip"'
    return response

# -----------------------------------------
# Download All files in group
# -----------------------------------------
@login_required
def delete_all_files_in_group(request, group_id):
    group = get_object_or_404(RecordGroup, id=group_id, patient__user=request.user)
    
    if request.method == 'POST':
        files = PatientFile.objects.filter(group=group)
        deleted_count = files.count()
        for f in files:
            f.delete()  # Ensures the physical file is deleted too
        messages.success(request, f"🗑️ Deleted {deleted_count} files from group '{group.name}'.")
        return redirect('patients:my_records')

    return redirect('patients:my_records')

# -----------------------------------------
# Download All zip file ungroup
# -----------------------------------------
@login_required
def download_ungrouped_zip(request):
    patient = get_object_or_404(Patient, user=request.user)
    files = PatientFile.objects.filter(patient=patient, group__isnull=True)
    if not files:
        messages.error(request, "No ungrouped files to download.")
        return redirect('patients:my_records')

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for f in files:
            if f.file:
                zip_file.writestr(f.title or os.path.basename(f.file.name), f.file.read())
    zip_buffer.seek(0)

    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="Ungrouped_Files.zip"'
    return response

# -----------------------------------------
# Delete All files in Ungroup
# -----------------------------------------
@login_required
def delete_all_ungrouped(request):
    patient = get_object_or_404(Patient, user=request.user)
    if request.method == "POST":
        PatientFile.objects.filter(patient=patient, group__isnull=True).delete()
        messages.success(request, "🗑️ All ungrouped files deleted successfully.")
    return redirect('patients:my_records')

