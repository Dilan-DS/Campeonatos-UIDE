"""Los widgets de un ModelForm solo pueden nombrar campos reales del modelo.

Varios formularios (CarreraForm, CampeonatoForm, JugadorForm, NoticiaForm,
PagoForm, CodigoQRForm, TransmisionForm) declaraban widgets para campos
como 'apellido', 'fecha_nacimiento', 'monto', 'beneficiario', 'titulo',
'url' o 'fecha_hora' que nunca existieron en el modelo correspondiente
-- resto de una version anterior. Django los ignora en silencio (no
revienta), asi que el bug pasaba desapercibido: el campo real se
renderizaba sin la clase CSS del sistema de diseño.
"""
from core.forms import (
    CampeonatoForm, CarreraForm, CodigoQRForm, EquipoForm, JugadorForm,
    NoticiaForm, PagoForm, TransmisionForm,
)
from core.tests.base import *  # noqa: F401,F403


class WidgetsDeFormulariosSoloNombranCamposReales(PruebaBase):

    FORMULARIOS = [
        CarreraForm, CampeonatoForm, EquipoForm, JugadorForm, NoticiaForm,
        PagoForm, CodigoQRForm, TransmisionForm,
    ]

    def test_ningun_widget_referencia_un_campo_inexistente(self):
        fantasmas = []
        for formulario_cls in self.FORMULARIOS:
            nombres_reales = {f.name for f in formulario_cls._meta.model._meta.get_fields()}
            widgets = getattr(formulario_cls.Meta, "widgets", {})
            for campo in widgets:
                if campo not in nombres_reales:
                    fantasmas.append(f"{formulario_cls.__name__}.{campo}")
        self.assertEqual(fantasmas, [],
                         "widgets para campos que no existen en el modelo: "
                         + ", ".join(fantasmas))
