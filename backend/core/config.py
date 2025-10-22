from pydantic import BaseModel
from pydantic_settings import BaseSettings

class DBSettings(BaseModel):
    url: str = "postgresql+asyncpg://postgres:postgres@db:5432/effective_mobile"
    echo: bool = False

class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    api_v1_prefix: str = "/api/v1"

settings = Settings()