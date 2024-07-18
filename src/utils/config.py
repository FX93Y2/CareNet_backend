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

SERVICE_AREAS = [
    [
        {"lat": 31.9399, "lon": 117.6816}, # 肥东
        {"lat": 31.7551, "lon": 117.3828}, # 包河
        {"lat": 31.6524, "lon": 116.9354}, # 肥西
    ],
]
settings = get_settings()