from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str
    db_name: str
    arcgis_api_key: str
    arcgis_portal_url: str

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()

settings = get_settings()