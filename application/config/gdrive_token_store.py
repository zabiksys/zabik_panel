"""SQLite token store for per-user Google Drive OAuth tokens."""
import json
import sqlite3
from pathlib import Path

from google.oauth2.credentials import Credentials

from application.config.config import Config, PANEL_CACHE_PATH


DB_PATH = Path(Config().get(PANEL_CACHE_PATH, 'config/panelindexcache')) / 'gdrive_tokens.db'


def _get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the tokens table if it doesn't exist."""
    with _get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS gdrive_tokens (
                username TEXT PRIMARY KEY,
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                token_expiry REAL,
                scopes TEXT,
                created_at REAL DEFAULT (unixepoch())
            )
        """)
        conn.commit()


def store_token(
    username: str,
    access_token: str,
    refresh_token: str | None,
    token_expiry: float | None,
    scopes: list[str],
) -> None:
    """Store or update a user's Google Drive OAuth token."""
    init_db()
    with _get_db() as conn:
        conn.execute(
            """
            INSERT INTO gdrive_tokens (username, access_token, refresh_token, token_expiry, scopes)
            VALUES (:username, :access_token, :refresh_token, :token_expiry, :scopes)
            ON CONFLICT(username) DO UPDATE SET
                access_token = excluded.access_token,
                refresh_token = excluded.refresh_token,
                token_expiry = excluded.token_expiry,
                scopes = excluded.scopes,
                created_at = excluded.created_at
            """,
            {
                "username": username,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_expiry": token_expiry,
                "scopes": json.dumps(scopes),
            },
        )
        conn.commit()


def get_token(username: str) -> Credentials | None:
    """Retrieve a user's stored Google Drive OAuth credentials.

    Returns ``None`` if no token exists.  Automatically refreshes an
    expired token when a *refresh_token* is available.
    """
    init_db()
    with _get_db() as conn:
        row = conn.execute(
            "SELECT * FROM gdrive_tokens WHERE username = ?", (username,)
        ).fetchone()

    if row is None:
        return None

    credentials = Credentials(
        token=row["access_token"],
        refresh_token=row["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=Config()["google_drive_oauth"]["client_id"],
        client_secret=Config()["google_drive_oauth"]["client_secret"],
        scopes=json.loads(row["scopes"]),
    )

    # Refresh silently if expired
    if credentials.expired and credentials.refresh_token:
        from google.auth.transport.requests import Request
        credentials.refresh(Request())
        store_token(
            username=username,
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_expiry=credentials.expiry.timestamp() if credentials.expiry else None,
            scopes=list(credentials.scopes) if credentials.scopes else [],
        )

    return credentials


def delete_token(username: str) -> None:
    """Remove a user's stored token (e.g. after revocation)."""
    init_db()
    with _get_db() as conn:
        conn.execute(
            "DELETE FROM gdrive_tokens WHERE username = ?", (username,)
        )
        conn.commit()
