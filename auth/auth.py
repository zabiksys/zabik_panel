from ms_active_directory import ADDomain, DomainConnectException
from pathlib import Path
from tornado.web import RequestHandler

import json
import tornado
import sys

sys.path.append(str(Path(__file__).parent))
from application.config.config import Config



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
        self.render("login.html", errormessage=errormessage, domain=Config()['active_directory']['domain'])

    def check_permission_old(self, username, password):
        if username == "bokeh" and password == "bokeh":
            return True
        return False

    def check_permission(self, domain, username, password):
        addomain = ADDomain(
            domain,
            encrypt_connections=False,
            ldap_servers_or_uris=Config()['active_directory']['ldap_uris'])
        username = domain + '\\' + username
        try:
            session = addomain.create_session_as_user(username, password)
            return True
        except DomainConnectException:
            return False

    def post(self):
        domain = self.get_argument("domain", "")
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        auth = self.check_permission(domain, username, password)
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
