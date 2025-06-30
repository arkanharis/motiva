from decouple import config

class Settings:
    DATABASE_URL: str = config("DATABASE_URL")
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    GOOGLE_CLIENT_ID: str = config("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = config("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = config("GOOGLE_REDIRECT_URI")

settings = Settings()