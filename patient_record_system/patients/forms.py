from django import forms
from .models import PatientFile, RecordGroup


class RecordGroupForm(forms.ModelForm):
    class Meta:
        model = RecordGroup
        fields = ['name']


class PatientFileUploadForm(forms.ModelForm):
    new_group_name = forms.CharField(
        max_length=255,
        required=False,
        label="Or Create New Group"
    )

    class Meta:
        model = PatientFile
        fields = ['title', 'description', 'file', 'group', 'new_group_name']

    def __init__(self, patient, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = patient.groups.all()
        self.fields['group'].required = False
        self.fields['title'].required = False


# ✅ Custom widget that supports multiple file selection
class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class BatchUploadForm(forms.Form):
    title = forms.CharField(required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    group = forms.ModelChoiceField(queryset=RecordGroup.objects.none(), required=False)
    new_group_name = forms.CharField(required=False)

    def __init__(self, patient=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if patient:
            self.fields['group'].queryset = patient.groups.all()
