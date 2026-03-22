import os


class Config:
    ENV: str = os.getenv("ENV", "development")
