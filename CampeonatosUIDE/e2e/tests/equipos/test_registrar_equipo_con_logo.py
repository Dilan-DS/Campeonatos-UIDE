"""Flujo real y pesado: un delegado sube un logo real al registrar su equipo.

Equipo.clean() exige un campeonato en estado INSCRIPCION y un logo (pese a
que el campo del modelo es blank=True): sin logo el submit falla en
silencio para el usuario si el formulario no se revisa con cuidado, asi
que vale la pena probarlo con un archivo real, no solo a nivel de forms.
"""
import io

import pytest
from PIL import Image

from core.tests.base import PWD, _campeonato_para_calendario


@pytest.mark.django_db
def test_delegado_registra_equipo_con_logo(page, live_server, datos, tmp_path):
    campeonato_abierto = _campeonato_para_calendario(
        "E2E abierto a inscripciones", datos["deporte"], ["LUNES"])

    logo_path = tmp_path / "logo.png"
    Image.new("RGB", (4, 4), color=(200, 30, 30)).save(logo_path, format="PNG")

    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "delegado_test")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")

    page.goto(f"{live_server.url}/equipos/registrar/?campeonato_id={campeonato_abierto.id}")
    page.fill("#id_nombre", "Equipo E2E con logo")
    page.select_option("#id_carrera", str(datos["carrera"].id))
    page.select_option("#id_genero", "masculino")
    page.set_input_files("#id_logo", str(logo_path))
    page.get_by_role("button", name="Registrar Equipo").click()

    page.wait_for_url(f"{live_server.url}/equipos/")
    assert "Equipo E2E con logo" in page.content()

    from core.models import Equipo
    equipo = Equipo.objects.get(nombre="Equipo E2E con logo")
    assert equipo.logo.name
    assert equipo.campeonato_id == campeonato_abierto.id


@pytest.mark.django_db
def test_sin_logo_el_formulario_no_pasa(page, live_server, datos):
    """Confirma que el navegador no manda el form sin logo como si fuera valido."""
    campeonato_abierto = _campeonato_para_calendario(
        "E2E sin logo", datos["deporte"], ["LUNES"])

    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "delegado_test")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")

    page.goto(f"{live_server.url}/equipos/registrar/?campeonato_id={campeonato_abierto.id}")
    page.fill("#id_nombre", "Equipo sin logo")
    page.select_option("#id_carrera", str(datos["carrera"].id))
    page.select_option("#id_genero", "masculino")
    page.get_by_role("button", name="Registrar Equipo").click()

    from core.models import Equipo
    assert not Equipo.objects.filter(nombre="Equipo sin logo").exists()
