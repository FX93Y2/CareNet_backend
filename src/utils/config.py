from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str
    db_name: str
    ARCGIS_API_KEY: str
    ARCGIS_PORTAL_URL: str
    SERVICE_AREA_LAYER_URL: str

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()