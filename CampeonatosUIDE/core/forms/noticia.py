from django import forms
from core.models import Noticia

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = '__all__'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Título de la noticia'}),
            'contenido': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Contenido de la noticia'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'file-input'}),
        }
