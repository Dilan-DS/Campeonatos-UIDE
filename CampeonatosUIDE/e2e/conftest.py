"""Fixtures compartidas por los tests E2E.

Arranca un servidor Django real (pytest-django `live_server`) y navega
contra el con Playwright. No usa mocks: cada test golpea la aplicacion de
verdad, con su propia base de datos de pruebas.
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CampeonatosUIDE.settings")

import django  # noqa: E402

django.setup()

from core.tests.base import PWD, _datos_base  # noqa: E402

__all__ = ["PWD"]


@pytest.fixture(autouse=True)
def _media_root_temporal(settings):
    """live_server sirve la app real: sin esto, cada logo/comprobante que
    sube un test de Playwright se escribe de verdad en el media/ del
    proyecto (los tests de Django ya se protegen igual en PruebaBase)."""
    settings.MEDIA_ROOT = tempfile.mkdtemp(prefix="uide_e2e_media_")


@pytest.fixture
def datos(db):
    """Mismo conjunto de datos base que usan los tests de Django.

    Reutilizar `_datos_base()` evita mantener dos fixtures distintas
    (usuarios, campeonato, equipos) para el mismo proposito.
    """
    return _datos_base()
