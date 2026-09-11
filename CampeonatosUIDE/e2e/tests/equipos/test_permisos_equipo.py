"""Caso negativo: rutas protegidas no deben ser accesibles sin sesion."""
import pytest

from core.tests.base import PWD


@pytest.mark.django_db
def test_listar_equipos_redirige_a_login_si_no_hay_sesion(page, live_server, datos):
    page.goto(f"{live_server.url}/equipos/")
    page.wait_for_url(lambda url: "/login/" in url)


@pytest.mark.django_db
def test_admin_ve_el_listado_de_equipos(page, live_server, datos):
    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "admin_test")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")
    page.wait_for_url(f"{live_server.url}/panel/admin/")

    page.goto(f"{live_server.url}/equipos/")
    assert "/login/" not in page.url
    assert datos["equipo"].nombre in page.content()
