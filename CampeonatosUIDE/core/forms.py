from django import forms
from django.utils.safestring import mark_safe
from .models import Equipo, Pago

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mostrar el QR si el campeonato tiene uno
        if self.instance.pk and self.instance.campeonato and self.instance.campeonato.codigo_qr:
            codigo_qr = self.instance.campeonato.codigo_qr
            self.fields['codigo_qr_info'] = forms.CharField(
                required=False,
                label="Código QR del campeonato",
                widget=forms.Textarea(attrs={'readonly': 'readonly', 'rows': 6}),
                initial=mark_safe(
                    f"<strong>Banco:</strong> {codigo_qr.banco}<br>"
                    f"<img src='{codigo_qr.imagen_qr.url}' width='200' style='border:1px solid #ccc; padding:5px'/>"
                )
            )


class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.codigo_qr and self.instance.codigo_qr.imagen_qr:
            self.fields['codigo_qr_preview'] = forms.CharField(
                required=False,
                label='Vista previa QR',
                widget=forms.Textarea(attrs={'readonly': 'readonly', 'rows': 6}),
                initial=mark_safe(
                    f"<strong>Banco:</strong> {self.instance.codigo_qr.banco}<br>"
                    f"<img src='{self.instance.codigo_qr.imagen_qr.url}' width='200' style='border:1px solid #ccc;'/>"
                )
            )