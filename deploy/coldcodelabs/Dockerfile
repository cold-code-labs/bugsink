# Vör — Bugsink da frota CCL com SSO Logto.
#
# Overlay FINO sobre a imagem oficial: só injeta a config de SSO (RemoteUser →
# identidade do oauth2-proxy/Logto). Zero rebuild do Bugsink. Base pinada por
# digest p/ reprodutibilidade — bumpar conscientemente ao seguir o upstream.
FROM bugsink/bugsink@sha256:bc3a491edb7d94d42ae49be14f586a4b7eefa929389272c37f9bec112f232e78

COPY bugsink_sso.py /app/bugsink_sso.py
COPY bugsink_sso_conf.py /app/bugsink_sso_conf.py

# Passa a usar o settings estendido (default do Bugsink + SSO).
ENV DJANGO_SETTINGS_MODULE=bugsink_sso_conf
