# Vör — Bugsink da frota CCL (fork com SSO Logto)

Overlay fino sobre a imagem oficial `bugsink/bugsink` que dá **SSO Logto** ao
Bugsink (que não tem OIDC nativo), eliminando o login duplo.

## Como funciona

```
browser → oauth2-proxy (OIDC → Logto / CCL ID) → Bugsink
                         │
                         └─ repassa X-Forwarded-Email ─┐
                                                       ▼
        ForwardedIdentityMiddleware + FleetSSOBackend  → auto-login
```

- `bugsink_sso.py` — middleware (`PersistentRemoteUserMiddleware` lendo
  `X-Forwarded-Email`) + backend que mapeia quem passa pelo Logto → superuser da
  frota. Dashboard compartilhado; auditoria por-pessoa é no Logto.
- `bugsink_sso_conf.py` — `from bugsink_conf import *` + injeção do middleware/
  backend. Ativado por `DJANGO_SETTINGS_MODULE=bugsink_sso_conf` (no Dockerfile).
- `Dockerfile` — `FROM bugsink/bugsink@<digest>` + COPY dos dois arquivos.

O **ingest** (`/api/<id>/...`) é exempt no oauth2-proxy (`SKIP_AUTH_ROUTES`), não
passa por SSO e segue autenticado só pelo DSN — os SDKs não são afetados.

## Build / deploy

```bash
docker build -t ghcr.io/cold-code-labs/bugsink:sso deploy/coldcodelabs
docker push ghcr.io/cold-code-labs/bugsink:sso
# Coolify app "vor" (surtr) → image = ghcr.io/cold-code-labs/bugsink:sso → redeploy
```

Requer no oauth2-proxy: `--pass-user-headers` (default) e
`OAUTH2_PROXY_OIDC_EMAIL_CLAIM=email`.
