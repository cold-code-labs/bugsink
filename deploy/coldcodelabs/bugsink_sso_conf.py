"""Settings da frota CCL = config padrão do Bugsink + SSO Logto.

Estende (não substitui) o `bugsink_conf.py` que a imagem oficial gera a partir
das envs — só injeta o middleware/backend de SSO. Ativado por
`DJANGO_SETTINGS_MODULE=bugsink_sso_conf` (setado no Dockerfile do overlay).
"""
from bugsink_conf import *  # noqa: F401,F403  (toda a config do Bugsink via envs)

# ── SSO Logto (oauth2-proxy → RemoteUser) ──────────────────────────────────────
# O middleware entra logo APÓS o AuthenticationMiddleware e ANTES do
# LoginRequiredMiddleware — senão o login-required redireciona pro login do
# Bugsink antes do auto-login acontecer.
MIDDLEWARE = list(MIDDLEWARE)  # noqa: F405
_auth_mw = "django.contrib.auth.middleware.AuthenticationMiddleware"
_sso_mw = "bugsink_sso.ForwardedIdentityMiddleware"
if _sso_mw not in MIDDLEWARE:
    MIDDLEWARE.insert(MIDDLEWARE.index(_auth_mw) + 1, _sso_mw)

# Backend de SSO na frente do ModelBackend (que segue valendo p/ break-glass local).
AUTHENTICATION_BACKENDS = ["bugsink_sso.FleetSSOBackend"] + [
    b for b in list(AUTHENTICATION_BACKENDS) if b != "bugsink_sso.FleetSSOBackend"  # noqa: F405
]
