"""CRUD real desde el navegador: un admin registra un Deporte nuevo.

Se elige Deporte por ser el formulario mas simple del proyecto (nombre +
descripcion, sin archivos ni campos dependientes), ideal para probar el
flujo de extremo a extremo sin acoplarse a reglas de negocio de otro modulo.
"""
import pytest

from core.models import Deporte
from core.tests.base import PWD


@pytest.mark.django_db
def test_admin_registra_un_deporte_nuevo(page, live_server, datos):
    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "admin_test")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")
    page.wait_for_url(f"{live_server.url}/panel/admin/")

    page.goto(f"{live_server.url}/deportes/registrar/")
    page.fill("#id_nombre", "Voleibol E2E")
    page.fill("#id_descripcion", "Creado por la prueba end-to-end.")
    page.get_by_role("button", name="Guardar Deporte").click()

    page.wait_for_url(f"{live_server.url}/deportes/")
    assert Deporte.objects.filter(nombre="Voleibol E2E").exists()
    assert "Voleibol E2E" in page.content()


@pytest.mark.django_db
def test_un_jugador_no_puede_registrar_deportes(page, live_server, datos):
    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "jugador_test")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")

    page.goto(f"{live_server.url}/deportes/registrar/")
    # La vista es admin-only (UserPassesTestMixin.test_func = es_admin): un
    # jugador nunca debe llegar a ver el formulario de alta.
    assert "id_nombre" not in page.content()
