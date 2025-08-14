from django import forms
from core.models import Suspension

class SuspensionForm(forms.ModelForm):
    class Meta:
        model = Suspension
        fields = '__all__'
        widgets = {
            'jugador': forms.Select(attrs={'class': 'select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'motivo': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Motivo de la suspensión'}),
        }
