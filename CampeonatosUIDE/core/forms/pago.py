from django import forms
from core.models import Pago, CodigoQR

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = '__all__'
        widgets = {
            'equipo': forms.Select(attrs={'class': 'select'}),
            'metodo': forms.Select(attrs={'class': 'select'}),
            'monto': forms.NumberInput(attrs={'class': 'input', 'step': '0.01'}),
            'fecha_pago': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'comprobante_pago': forms.ClearableFileInput(attrs={'class': 'file-input'}),
            'estado': forms.Select(attrs={'class': 'select'}),
            'observacion_admin': forms.Textarea(attrs={'class': 'textarea', 'placeholder': 'Observaciones del administrador'}),
            'codigo_qr': forms.Select(attrs={'class': 'select'}),
        }

class PagoDelegadoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['equipo', 'metodo', 'codigo_qr', 'comprobante_pago']
        widgets = {
            'equipo': forms.Select(attrs={'class': 'select'}),
            'metodo': forms.Select(attrs={'class': 'select'}),
            'comprobante_pago': forms.ClearableFileInput(attrs={'class': 'file-input'}),
            'codigo_qr': forms.Select(attrs={'class': 'select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo')
        codigo_qr = cleaned_data.get('codigo_qr')

        if metodo == 'TRANSFERENCIA' and not codigo_qr:
            self.add_error('codigo_qr', 'Debe seleccionar un código QR para transferencias.')
        return cleaned_data

class CodigoQRForm(forms.ModelForm):
    class Meta:
        model = CodigoQR
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre del QR'}),
            'imagen_qr': forms.ClearableFileInput(attrs={'class': 'file-input'}),
            'banco': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Banco'}),
            'tipo_cuenta': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tipo de cuenta'}),
            'numero_cuenta': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Número de cuenta'}),
            'beneficiario': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Beneficiario'}),
            'identificacion': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Identificación'}),
            'visible_delegado': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }
