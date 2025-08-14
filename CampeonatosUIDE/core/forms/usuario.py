from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth import get_user_model
from core.models import Usuario

class RegistroUsuarioForm(UserCreationForm):
    ROL_CHOICES = [
        ('JUGADOR', 'Jugador'),
        ('DELEGADO', 'Delegado'),
    ]
    rol = forms.ChoiceField(label='Rol', choices=ROL_CHOICES, widget=forms.RadioSelect)
    cedula = forms.CharField(required=True, max_length=10, label="Cédula", help_text="10 dígitos.")

    class Meta:
        model = Usuario
        fields = (
            'username', 'first_name', 'last_name', 'email', 'cedula',
            'carrera', 'genero', 'rol',
            'password1', 'password2',
        )
        labels = {
            'username':   'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name':  'Apellidos',
            'email':      'Correo electrónico',
            'carrera':    'Carrera',
            'genero':     'Género',
            'rol':        'Rol',
            'password1':  'Contraseña',
            'password2':  'Confirmar contraseña',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input',  'placeholder': 'Ej. jlopez'}),
            'first_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tu nombre'}),
            'last_name':  forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tus apellidos'}),
            'email':      forms.EmailInput(attrs={'class': 'input', 'placeholder': 'tucorreo@ejemplo.com'}),
            'carrera': forms.Select(attrs={'class': 'select'}),
            'genero':  forms.Select(attrs={'class': 'select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['password1'].widget.attrs.update({'class': 'input'})
        self.fields['password2'].widget.attrs.update({'class': 'input'})
        self.fields['password1'].help_text = (
            "• Mínimo 8 caracteres.<br>"
            "• No uses algo muy común.<br>"
            "• No puede ser completamente numérica."
        )
        self.fields['password2'].help_text = "Repite la contraseña exactamente igual."

    def clean_cedula(self):
        ced = (self.cleaned_data.get("cedula") or "").strip()
        if not ced.isdigit() or len(ced) != 10:
            raise ValidationError("La cédula debe tener exactamente 10 dígitos.")
        if Usuario.objects.filter(cedula__iexact=ced).exists():
            raise ValidationError("Esta cédula ya está registrada.")
        return ced

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = self.cleaned_data.get('rol')
        user.email = (self.cleaned_data.get('email') or '').lower()
        user.cedula = self.cleaned_data["cedula"].strip()
        if commit:
            user.save()
        return user


class CrearUsuarioAdminForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'rol', 'carrera', 'genero',
            'password1', 'password2',
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'rol': forms.Select(attrs={'class': 'select'}),
            'carrera': forms.Select(attrs={'class': 'select'}),
            'genero': forms.Select(attrs={'class': 'select'}),
        }


class CrearUsuarioDelegadoForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'carrera', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'carrera': forms.Select(attrs={'class': 'select'}),
            'password': forms.PasswordInput(attrs={'class': 'input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.rol = 'DELEGADO'
        if commit:
            user.save()
        return user


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'cedula', 'rol']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'cedula': forms.TextInput(attrs={'class': 'input'}),
            'rol': forms.Select(attrs={'class': 'input'}),
        }


class PerfilUsuarioForm(forms.ModelForm):
    cedula = forms.CharField(required=True, max_length=10, label="Cédula")

    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "email", "cedula", "carrera", "genero"]

    def clean_cedula(self):
        ced = (self.cleaned_data.get("cedula") or "").strip()
        if not ced.isdigit() or len(ced) != 10:
            raise ValidationError("La cédula debe tener exactamente 10 dígitos.")
        qs = Usuario.objects.filter(cedula__iexact=ced).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Esta cédula ya está registrada.")
        return ced

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = Usuario.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ese correo ya está en uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = (user.email or "").lower()
        if commit:
            user.save()
        return user


class PasswordResetConValidacionForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        U = get_user_model()
        if not U.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("No existe una cuenta activa con ese correo.")
        return email