from django import forms
from core.models import Deporte

class DeporteForm(forms.ModelForm):
    class Meta:
        model = Deporte
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre del deporte'}),
            'descripcion': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Descripción del deporte'}),
        }
