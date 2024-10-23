from django import forms
from .models import WorkoutPlan

class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ['duration', 'target_area', 'equipment', 'custom_target', 'custom_equipment']
        widgets = {
            'duration': forms.Select(attrs={'class': 'form-control'}),
            'target_area': forms.Select(attrs={'class': 'form-control'}),
            'equipment': forms.Select(attrs={'class': 'form-control'}),
            'custom_target': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_equipment': forms.TextInput(attrs={'class': 'form-control'}),
        }