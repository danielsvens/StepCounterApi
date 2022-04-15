import os


class Settings:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DEBUG = False
    TESTING = False
    DB_USERNAME = os.environ.get("DB_USERNAME", 'postgresUser')
    DB_PASSWORD = os.environ.get("DB_PASSWORD", 'postgresPassword')
    DB_HOST = os.environ.get("DB_HOST", '192.168.1.4')
    DB_PORT = os.environ.get("DB_PORT", '32014')
    DB_NAME = os.environ.get("DB_NAME", 'steps')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_RELOADER = False
    ENV = 'production'
    PORT = 8082
    SECRET = 'Super le secret '

    ## EDMQ CONFIG
    EDMQ_URL = os.environ.get('EDMQ_URL', 'edmq://guest:guest@192.168.1.4:32021')

settings = Settings()
