from django import forms
from django.core.exceptions import ValidationError

from core.models import Usuario, Arbitro
from core.validators import validate_ecuadorian_cedula

class ArbitroForm(forms.ModelForm):
    cedula = forms.CharField(required=False, max_length=10, validators=[validate_ecuadorian_cedula])
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'cedula', 'genero', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Correo electrónico'}),
            'first_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Apellidos'}),
            'cedula': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Cédula'}),
            'genero': forms.Select(attrs={'class': 'select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }

from django.db import transaction
from core.models import Deporte

class CrearUsuarioArbitroForm(forms.ModelForm):
    cedula = forms.CharField(required=True, max_length=10, validators=[validate_ecuadorian_cedula])
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}), label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'input'}), label="Confirmar Contraseña")

    # Campos del modelo Arbitro
    experiencia = forms.CharField(widget=forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Años de experiencia, torneos dirigidos, etc.'}), label="Experiencia", required=False)
    contacto = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Número de teléfono o email de contacto'}), label="Contacto")
    deportes = forms.ModelMultipleChoiceField(
        queryset=Deporte.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Deportes que puede arbitrar"
    )
    estado = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput(attrs={'class': 'checkbox'}), label="Activo")

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'cedula', 'genero', 'password', 'confirm_password', 'experiencia', 'contacto', 'deportes', 'estado']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre de usuario'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Correo electrónico'}),
            'first_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Apellidos'}),
            'cedula': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Cédula'}),
            'genero': forms.Select(attrs={'class': 'select'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("Ya existe un usuario con este nombre de usuario.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este correo electrónico.")
        return email

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula and Usuario.objects.filter(cedula=cedula).exists():
            raise ValidationError("Ya existe un usuario con esta cédula.")
        return cedula

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError({"confirm_password": "Las contraseñas no coinciden."})
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.rol = 'ARBITRO'
        if commit:
            user.save()
            arbitro = Arbitro.objects.create(
                usuario=user,
                experiencia=self.cleaned_data['experiencia'],
                contacto=self.cleaned_data['contacto'],
                estado=self.cleaned_data['estado']
            )
            arbitro.deportes.set(self.cleaned_data['deportes'])
        return user
