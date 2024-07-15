from pydantic import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str
    db_name: str

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()