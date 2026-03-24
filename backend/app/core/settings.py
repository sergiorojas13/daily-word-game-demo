from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "portal_juegos_backend"
    app_host: str = "0.0.0.0"
    app_port: int = 0000
    app_env: str = "dev"

    sql_server: str
    sql_database: str
    sql_user: str
    sql_password: str
    sql_driver: str = "ODBC Driver 17 for SQL Server"
    sql_trust_server_certificate: str = "yes"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

