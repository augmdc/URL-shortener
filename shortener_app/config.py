from functools import lru_cache

from pydantic import BaseSettings

class Settings(BaseSettings):
    env_name: str = "Local"
    db_url: str = "sqlite:///./shortener.db"
    base_url: str = "http://localhost/"
    
    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for: {settings.env_name}")
    return settings

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    print(f"Loading settings for: {settings.env_name}")
    return settings