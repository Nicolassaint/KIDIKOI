from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HF_TOKEN: str
    MODEL_NAME: str
    DIARIZATION_MODEL: str
    
    class Config:
        env_file = ".env"

settings = Settings() 