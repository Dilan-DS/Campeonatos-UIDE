"""Configuracion compartida de los tests E2E.

Nota importante: este proyecto usa `pytest-playwright` (Python), no el
`@playwright/test` de Node. En el ecosistema Python no existe un
`playwright.config.py` que Playwright lea automaticamente como en Node: la
configuracion real vive en `pytest.ini` (DJANGO_SETTINGS_MODULE, rutas de
test) y en `e2e/conftest.py` (fixtures `base_url`, `datos_base`, etc). Este
archivo solo agrupa las constantes que usan los tests, para no repetirlas
ni inventar un mecanismo de configuracion que Python no tiene.
"""

# Timeout de espera por defecto para acciones de Playwright (ms).
TIMEOUT_ACCION_MS = 10_000

# Viewport usado en todos los tests, salvo que un test lo cambie a proposito
# (por ejemplo para probar el menu movil).
VIEWPORT = {"width": 1280, "height": 800}
