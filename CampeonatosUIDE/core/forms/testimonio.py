from django import forms
from core.models import Testimonio

class TestimonioForm(forms.ModelForm):
    class Meta:
        model = Testimonio
        fields = '__all__'
        widgets = {
            'autor': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Autor del testimonio'}),
            'contenido': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Contenido del testimonio'}),
            'fecha': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'aprobado': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }
