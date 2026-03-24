from __future__ import annotations

from urllib.parse import quote_plus

import pyodbc

from app.core.settings import settings


def build_connection_string() -> str:
    parts = [
        f"DRIVER={{{settings.sql_driver}}}",
        f"SERVER={settings.sql_server}",
        f"DATABASE={settings.sql_database}",
        f"UID={settings.sql_user}",
        f"PWD={settings.sql_password}",
        f"TrustServerCertificate={settings.sql_trust_server_certificate}",
    ]
    return ";".join(parts)


def get_connection() -> pyodbc.Connection:
    connection_string = build_connection_string()
    return pyodbc.connect(connection_string, timeout=10)


def get_connection_string_masked() -> str:
    parts = [
        f"DRIVER={{{settings.sql_driver}}}",
        f"SERVER={settings.sql_server}",
        f"DATABASE={settings.sql_database}",
        f"UID={settings.sql_user}",
        "PWD=********",
        f"TrustServerCertificate={settings.sql_trust_server_certificate}",
    ]
    return ";".join(parts)
