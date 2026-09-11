"""Paquete de vistas.

Este fichero encadenaba dieciocho `from .x_views import *` para que
core/urls.py pudiera hacer `from .views import *`. Esa cadena tenia un
efecto silencioso: cuando dos modulos definian una funcion con el mismo
nombre, la del modulo importado despues se quedaba con el nombre y la otra
dejaba de existir. Asi quedaron inalcanzables `detalle_equipo` de
jugador_views y `registrar_resultado_partido` de arbitro_views, con
aspecto de codigo en uso.

Ya no hace falta: urls.py importa cada vista de su modulo, y los modulos
que se necesitan entre si lo hacen con imports explicitos
(`from core.views.campeonato_views import es_admin_o_delegado`).

Se deja vacio a proposito. Si alguna vez hace falta reexportar algo, que
sea por nombre y no con un comodin.
"""
