"""Portada publica y listado de campeonatos publicos, sin sesion iniciada."""
import pytest
from playwright.sync_api import expect


@pytest.mark.django_db
def test_portada_publica_carga_sin_login(page, live_server, datos):
    page.goto(live_server.url + "/")
    assert page.title() != ""
    # La portada muestra el campeonato publico creado en _datos_base().
    expect(page.locator("body")).to_contain_text(datos["campeonato"].nombre)


@pytest.mark.django_db
def test_listado_de_campeonatos_publicos_no_exige_login(page, live_server, datos):
    respuesta = page.goto(f"{live_server.url}/campeonatos/publicos/")
    assert respuesta.status < 400
    expect(page.locator("body")).to_contain_text(datos["campeonato"].nombre)
