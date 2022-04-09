import os


class Settings:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DEBUG = False
    TESTING = False
    DB_USERNAME = os.environ.get("DB_USERNAME", '')
    DB_PASSWORD = os.environ.get("DB_PASSWORD", '')
    DB_HOST = os.environ.get("DB_HOST", 'postgresql-service')
    DB_PORT = os.environ.get("DB_PORT", '5432')
    DB_NAME = os.environ.get("DB_NAME", 'steps')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_RELOADER = False
    ENV = 'production'
    PORT = 8082


settings = Settings()
