from django import forms
from core.models import ImagenGaleria


class ImagenGaleriaForm(forms.ModelForm):
    class Meta:
        model = ImagenGaleria
        fields = "__all__"
        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "input",
                "placeholder": "Título de la imagen"
            }),
            "imagen": forms.ClearableFileInput(attrs={
                "class": "file-input",
                "accept": "image/*"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "textarea",
                "placeholder": "Descripción opcional",
                "rows": 3
            }),
        }
