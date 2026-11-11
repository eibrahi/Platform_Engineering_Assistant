from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    database_url: str
    test_database_url: str | None = None
    openai_chat_model: str | None = None
    openai_api_key: SecretStr | None = None


settings = Settings()
