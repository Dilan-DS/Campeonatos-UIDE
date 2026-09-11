"""Un arbitro carga el acta de su partido desde el navegador.

El equipo de _datos_base() no tiene jugadores en el roster (salvo el
titular del propio jugador de prueba, que juega en otro equipo), asi
que el acta no genera campos dinamicos por jugador y el resultado debe
cuadrar en 0-0 para pasar la validacion de "la suma de goles coincide
con el marcador" (ver core/views/arbitro_views.py).
"""
import pytest

from core.tests.base import PWD


@pytest.mark.django_db
def test_arbitro_cierra_el_acta_con_marcador_0_0(page, live_server, datos):
    partido = datos["partido"]

    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "arbitro_test")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")

    page.goto(f"{live_server.url}/arbitro/partido/{partido.id}/acta/")
    page.fill("#id_resultado_local", "0")
    page.fill("#id_resultado_visitante", "0")
    page.click("#acta-form button[type=submit]")

    page.wait_for_timeout(500)
    partido.refresh_from_db()
    assert partido.estado == "FINALIZADO"
    assert (partido.resultado_local, partido.resultado_visitante) == (0, 0)


@pytest.mark.django_db
def test_un_arbitro_no_puede_cargar_el_acta_de_otro_partido(page, live_server, datos):
    from core.models import Arbitro, Partido, Usuario
    from core.tests.base import _campeonato_para_calendario, _equipos_para_calendario

    otro_arbitro_usuario = Usuario.objects.create_user(
        username="arbitro_ajeno_e2e", email="aae@uide.edu.ec", password=PWD,
        rol="ARBITRO", carrera=datos["carrera"], genero="masculino")
    Arbitro.objects.create(usuario=otro_arbitro_usuario, experiencia="", contacto="")

    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "arbitro_ajeno_e2e")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")

    # No es 403: acta_partido_arbitro redirige con un mensaje de error a
    # detalle_partido, que a su vez es solo-admin y redirige de nuevo.
    page.goto(f"{live_server.url}/arbitro/partido/{datos['partido'].id}/acta/")
    assert "#id_resultado_local" not in page.content()
    datos["partido"].refresh_from_db()
    assert datos["partido"].estado == "PROGRAMADO"
