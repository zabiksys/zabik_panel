from ms_active_directory import ADDomain
from ms_active_directory.exceptions import MsActiveDirectoryException
from pathlib import Path
from tornado.web import RequestHandler

import json
import logging
import tornado
import sys

sys.path.append(str(Path(__file__).parent))
from application.config.config import Config

logger = logging.getLogger(__name__)


def _normalize_username(username: str) -> str:
    """Acepta `usuario`, `DOMINIO\\usuario` o `usuario@dominio` y devuelve solo el usuario."""
    if '\\' in username:
        username = username.split('\\', 1)[1]
    elif '@' in username:
        username = username.split('@', 1)[0]
    return username


def _ad_settings() -> dict:
    """Devuelve la configuración de AD normalizada.

    `domain` es el nombre DNS del dominio (se usa para localizar el dominio y
    construir los DN). Para el bind simple contra AD hay dos formatos válidos:

    - `upn`: `usuario@local.zabik`, usa el DNS y no necesita NetBIOS.
    - `netbios`: `DOMINIO\\usuario` (down-level), necesita `netbios_name`
      porque el nombre NetBIOS no tiene por qué coincidir con el DNS
      (p.ej. DNS `local.zabik` vs NetBIOS `DOMGSMNT`).

    Compatibilidad con configuraciones antiguas:
    - Si no existe `login_format`, se deduce: `netbios` cuando `domain` no
      tiene punto (p.ej. `DOMGSMNT`) o hay `netbios_name`; `upn` en caso
      contrario.
    - Si no existe `encrypt_connections`, se usa LDAP plano (como antes).
    """
    ad_config = dict(Config()['active_directory'])
    login_format = ad_config.get('login_format')
    if not login_format:
        domain = str(ad_config.get('domain', ''))
        if ad_config.get('netbios_name') or (domain and '.' not in domain):
            login_format = 'netbios'
        else:
            login_format = 'upn'
    ad_config['login_format'] = str(login_format).lower()
    return ad_config


def _ad_username(username: str, ad_config: dict) -> str:
    """Construye el nombre de usuario para el bind según el formato configurado."""
    username = _normalize_username(username)
    if ad_config['login_format'] == 'netbios':
        netbios_name = ad_config.get('netbios_name') or ad_config['domain']
        return netbios_name + '\\' + username
    return username + '@' + ad_config['domain']



# could define get_user_async instead
def get_user(request_handler):
    #return request_handler.get_cookie("user")
    user = request_handler.get_secure_cookie("user")
    if user:
        username = json.loads(user.decode('utf8'))
        path = request_handler.request.path
        if not path.startswith('/assets') \
            and not path.startswith('/notebooks') \
            and path != '/' \
            and not [app for app in Config()['users'].get(username, {'apps': []})['apps']
                     if request_handler.request.path.startswith('/' + app)]:
            request_handler.redirect('/')
    return user

# could also define get_login_url function (but must give up LoginHandler)
login_url = "/login"

# optional login page for login_url
class LoginHandler(RequestHandler):

    def get(self):
        try:
            errormessage = self.get_argument("error")
        except Exception:
            errormessage = ""
        self.render("login.html", errormessage=errormessage)

    def check_permission(self, username, password):
        ad_config = _ad_settings()
        dns_domain = ad_config['domain']
        extra = {}
        if ad_config.get('netbios_name'):
            extra['netbios_name'] = ad_config['netbios_name']
        addomain = ADDomain(
            dns_domain,
            # Por defecto LDAP plano: así una configuración antigua sin la clave
            # se comporta como antes. Las configuraciones nuevas deben poner
            # `encrypt_connections: true`.
            encrypt_connections=ad_config.get('encrypt_connections', False),
            ldap_servers_or_uris=ad_config['ldap_uris'],
            **extra)
        user = _ad_username(username, ad_config)
        try:
            addomain.create_session_as_user(user, password)
            return True
        except MsActiveDirectoryException:
            logger.warning('Login fallido para %s contra %s', user, dns_domain)
            return False
        except Exception:
            logger.exception('Error inesperado autenticando a %s', user)
            return False

    def post(self):
        username = _normalize_username(self.get_argument("username", ""))
        password = self.get_argument("password", "")
        auth = self.check_permission(username, password)
        if auth:
            self.set_current_user(username)
            self.redirect("/")
        else:
            error_msg = "?error=" + tornado.escape.url_escape("Login incorrect")
            self.redirect(login_url + error_msg)

    def set_current_user(self, user):
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
            #self.set_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")


# optional logout_url, available as curdoc().session_context.logout_url
logout_url = "/logout"


# optional logout handler for logout_url
class LogoutHandler(RequestHandler):

    def get(self):
        self.clear_cookie("user")
        self.redirect("/")
