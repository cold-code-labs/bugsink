"""SSO da frota CCL — identidade do oauth2-proxy (Logto) → login automático.

O Bugsink não tem OIDC nativo. Em vez de forkar o código, a frota o roda atrás
de um oauth2-proxy que autentica no Logto (CCL ID) e repassa a identidade em
`X-Forwarded-Email`. Este módulo faz o Django CONFIAR nesse header e logar o
usuário sozinho — acaba o login duplo (Logto + login do Bugsink).

Modelo: quem passa pelo Logto opera como o SUPERUSER da frota (dashboard
compartilhado; a auditoria por-pessoa vive no Logto). Isso evita provisionar
membership de team/project por pessoa e garante que a tela já abre "redonda"
(com os projetos do admin). O ingest (`/api/<id>/...`) é exempt no oauth2-proxy,
não passa por aqui e continua autenticado só pelo DSN.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.middleware import PersistentRemoteUserMiddleware


class ForwardedIdentityMiddleware(PersistentRemoteUserMiddleware):
    """Lê a identidade repassada pelo oauth2-proxy. `Persistent` = não desloga
    em requisições sem o header (ex.: o próprio ingest), só faz auto-login quando
    ele está presente."""

    header = "HTTP_X_FORWARDED_EMAIL"

    def process_request(self, request):
        # Fallback pro subject do Logto se o claim `email` não vier.
        if not request.META.get(self.header) and request.META.get("HTTP_X_FORWARDED_USER"):
            request.META[self.header] = request.META["HTTP_X_FORWARDED_USER"]
        return super().process_request(request)


class FleetSSOBackend(RemoteUserBackend):
    """Qualquer identidade que o Logto deixou passar entra como o superuser da
    frota. (O gate real de quem-pode é o oauth2-proxy/Logto, não o Bugsink.)"""

    def authenticate(self, request, remote_user=None):
        if not remote_user:
            return None
        User = get_user_model()
        return User.objects.filter(is_superuser=True, is_active=True).order_by("id").first()
