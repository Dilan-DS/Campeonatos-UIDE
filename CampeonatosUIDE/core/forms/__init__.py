from .carrera import CarreraForm
from .deporte import DeporteForm
from .campeonato import CampeonatoForm
from .equipo import EquipoForm, JugadorForm
from .partido import PartidoForm, ArbitroActaForm
from .pago import PagoForm, PagoDelegadoForm, CodigoQRForm
from .transmision import TransmisionForm
from .noticia import NoticiaForm
from .galeria import ImagenGaleriaForm
from .testimonio import TestimonioForm
from .usuario import (
    RegistroUsuarioForm,
    CrearUsuarioAdminForm,
    CrearUsuarioDelegadoForm,
    UsuarioForm,
    PerfilUsuarioForm,
    PasswordResetConValidacionForm
)
from .arbitro import ArbitroForm, CrearUsuarioArbitroForm
from .suspension import SuspensionForm
# Estadísticas
from .estadisticas.futbol import EstadisticaJugadorFutbolForm
from .estadisticas.basquet import EstadisticaJugadorBasquetForm
from .estadisticas.ajedrez import EstadisticaJugadorAjedrezForm
from .estadisticas.ecuaboly import EstadisticaJugadorEcuabolyForm
from .estadisticas.pingpong import EstadisticaJugadorPingPongForm
from .estadisticas.tenis import EstadisticaJugadorTenisForm
from .estadisticas.videojuegos import EstadisticaJugadorVideojuegosForm
from .estadisticas.futbolin import EstadisticaJugadorFutbolinForm

__all__ = [
    "CarreraForm","DeporteForm","CampeonatoForm","EquipoForm","JugadorForm",
    "PartidoForm","ArbitroActaForm","PagoForm","PagoDelegadoForm","CodigoQRForm",
    "TransmisionForm","NoticiaForm","ImagenGaleriaForm","TestimonioForm",
    "RegistroUsuarioForm","CrearUsuarioAdminForm","CrearUsuarioDelegadoForm",
    "UsuarioForm","PerfilUsuarioForm","PasswordResetConValidacionForm",
    "ArbitroForm","CrearUsuarioArbitroForm","SuspensionForm",
    "EstadisticaJugadorFutbolForm","EstadisticaJugadorBasquetForm",
    "EstadisticaJugadorAjedrezForm","EstadisticaJugadorEcuabolyForm",
    "EstadisticaJugadorPingPongForm","EstadisticaJugadorTenisForm",
    "EstadisticaJugadorVideojuegosForm","EstadisticaJugadorFutbolinForm",
]
