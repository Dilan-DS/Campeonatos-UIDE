"""Flujo real: un delegado paga por transferencia y sube el comprobante.

El QR principal se auto-selecciona (campo oculto para el rol DELEGADO,
ver RegistrarPagoDelegadoView), asi que el navegador solo tiene que
elegir el metodo y adjuntar la imagen del comprobante.
"""
import pytest
from PIL import Image

from core.tests.base import PWD


@pytest.mark.django_db
def test_delegado_paga_por_transferencia_con_comprobante(page, live_server, datos, tmp_path):
    comprobante_path = tmp_path / "comprobante.png"
    Image.new("RGB", (4, 4), color=(30, 200, 30)).save(comprobante_path, format="PNG")

    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "delegado_test")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")

    page.goto(f"{live_server.url}/delegado/pagos/registrar/")
    page.select_option("#id_metodo", "TRANSFERENCIA")
    page.set_input_files("#id_comprobante_pago", str(comprobante_path))
    page.get_by_role("button", name="Guardar Cambios").click()

    page.wait_for_url(f"{live_server.url}/delegado/pagos/detalle/")

    from core.models import Pago
    pago = Pago.objects.get(equipo=datos["equipo"])
    assert pago.metodo == "TRANSFERENCIA"
    assert pago.codigo_qr_id is not None
    assert pago.comprobante_pago.name


@pytest.mark.django_db
def test_delegado_paga_en_efectivo_sin_qr(page, live_server, datos):
    page.goto(f"{live_server.url}/login/")
    page.fill("#id_username", "delegado_test")
    page.fill("#id_password", PWD)
    page.click("button[type=submit]")

    page.goto(f"{live_server.url}/delegado/pagos/registrar/")
    page.select_option("#id_metodo", "EFECTIVO")
    page.get_by_role("button", name="Guardar Cambios").click()

    page.wait_for_url(f"{live_server.url}/delegado/pagos/detalle/")

    from core.models import Pago
    pago = Pago.objects.get(equipo=datos["equipo"])
    assert pago.metodo == "EFECTIVO"
    assert pago.codigo_qr_id is None
