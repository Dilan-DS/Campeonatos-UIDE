"""Login/logout reales, contra el formulario y las URLs de core/urls.py."""
import pytest
from playwright.sync_api import expect

from core.tests.base import PWD


@pytest.mark.django_db
def test_login_exitoso_redirige_al_dashboard_admin(page, live_server, datos):
    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "admin_test")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")
    page.wait_for_url(f"{live_server.url}/panel/admin/")
    expect(page.locator("body")).not_to_contain_text("No pudimos iniciar tu sesión")


@pytest.mark.django_db
def test_login_con_password_incorrecta_muestra_error_y_no_entra(page, live_server, datos):
    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "admin_test")
    page.fill("#id_password", "clave-incorrecta-cualquiera")
    page.click("button[type=submit]")
    expect(page.locator("text=No pudimos iniciar tu sesión")).to_be_visible()
    assert page.url.rstrip("/") == f"{live_server.url}/login".rstrip("/")


@pytest.mark.django_db
def test_logout_vuelve_a_pedir_login(page, live_server, datos):
    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "admin_test")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")
    page.wait_for_url(f"{live_server.url}/panel/admin/")

    page.goto(f"{live_server.url}/logout/")
    page.goto(f"{live_server.url}/panel/admin/")
    page.wait_for_url(lambda url: "/login/" in url)
