"""Google Drive OAuth 2.0 helpers for per-user authorization.

The flow works like this:

1.  Panel app calls ``get_authorization_url(username)`` and opens the URL
    in the user's browser.
2.  User grants access on Google's consent screen.
3.  Google redirects to ``/gdrive_callback`` handled by
    :class:`GDriveCallbackHandler`.
4.  The handler exchanges the authorization code for tokens and stores
    them in SQLite via :mod:`gdrive_token_store`.
5.  On subsequent requests the app calls ``get_credentials(username)`` which
    returns a ready-to-use :class:`google.oauth2.credentials.Credentials`
    object (with automatic silent refresh).

Configuration required in ``config/.secrets.yaml`` under the key
``google_drive_oauth``:

.. code-block:: yaml

    google_drive_oauth:
      client_id:     "YOUR_CLIENT_ID.apps.googleusercontent.com"
      client_secret: "YOUR_CLIENT_SECRET"
      redirect_uri:  "http://HOST:PORT/gdrive_callback"

The *redirect_uri* must match exactly what is registered in the Google Cloud
Console for this OAuth client.
"""
import base64
import json
import urllib.parse
import uuid

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from tornado.web import RequestHandler

from application.config.config import Config
from application.config.gdrive_token_store import get_token, store_token


SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def _get_oauth_config() -> dict:
    """Return the ``google_drive_oauth`` section from secrets."""
    return Config()["google_drive_oauth"]


def _make_flow() -> Flow:
    """Build a :class:`Flow` from the secrets file."""
    cfg = _get_oauth_config()
    return Flow.from_client_config(
        {
            "web": {
                "client_id": cfg["client_id"],
                "client_secret": cfg["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [cfg["redirect_uri"]],
            }
        },
        scopes=SCOPES,
        redirect_uri=cfg["redirect_uri"],
    )


def get_authorization_url(username: str) -> str:
    """Return the Google OAuth URL the user must visit.

    The *username* is embedded in the ``state`` parameter so the callback
    handler knows which Panel user completed the flow.
    """
    flow = _make_flow()
    state = base64.urlsafe_b64encode(json.dumps({"u": username}).encode()).decode().rstrip("=")
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=state,
        prompt="consent",          # always ask so we get a refresh_token
    )
    return authorization_url


def get_credentials(username: str) -> Credentials | None:
    """Return valid credentials for *username* or ``None``.

    Automatically refreshes an expired token when possible.
    """
    creds = get_token(username)
    if creds is None:
        return None

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        store_token(
            username=username,
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            token_expiry=creds.expiry.timestamp() if creds.expiry else None,
            scopes=list(creds.scopes) if creds.scopes else [],
        )

    return creds


class GDriveCallbackHandler(RequestHandler):
    """Tornado handler for ``/gdrive_callback``.

    Receives the authorization code from Google, exchanges it for tokens,
    stores them in the local SQLite DB and redirects the user back to the
    Panel application they came from.
    """

    def get(self):
        code = self.get_argument("code", None)
        state_b64 = self.get_argument("state", "")
        error = self.get_argument("error", None)

        if error:
            self._render_error(f"Google OAuth error: {error}")
            return

        if not code:
            self._render_error("Missing authorization code from Google.")
            return

        # Decode username from state
        try:
            padding = 4 - len(state_b64) % 4
            if padding != 4:
                state_b64 += "=" * padding
            state = json.loads(base64.urlsafe_b64decode(state_b64))
            username = state["u"]
        except Exception:
            self._render_error("Invalid OAuth state parameter.")
            return

        try:
            flow = _make_flow()
            flow.fetch_token(code=code)
            creds = flow.credentials

            store_token(
                username=username,
                access_token=creds.token,
                refresh_token=creds.refresh_token,
                token_expiry=creds.expiry.timestamp() if creds.expiry else None,
                scopes=list(creds.scopes) if creds.scopes else [],
            )
        except Exception as exc:
            self._render_error(f"Failed to exchange token: {exc}")
            return

        # Redirect back to the Panel app
        cfg = _get_oauth_config()
        panel_base = cfg.get("panel_base_url", "")
        if panel_base:
            self.redirect(f"{panel_base}/export_item")
        else:
            self._render_success(username)

    def _render_error(self, message: str):
        self.set_status(400)
        self.write(
            f"""<html><body>
            <h2>Authorization failed</h2>
            <p>{message}</p>
            <p><a href="javascript:window.close()">Close window</a></p>
            </body></html>"""
        )

    def _render_success(self, username: str):
        self.write(
            f"""<html><body>
            <h2>Google Drive connected</h2>
            <p>User <strong>{username}</strong> is now authorized.</p>
            <p>You can close this window and return to the Panel app.</p>
            <script>setTimeout(function(){{ window.close(); }}, 2000);</script>
            </body></html>"""
        )
