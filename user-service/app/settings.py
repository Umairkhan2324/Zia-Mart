from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)
SECRET_KEY = config("SECRET_KEY", cast=str)
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24
KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str)

BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)

KAFKA_CONSUMER_GROUP_ID_FOR_USER = config("KAFKA_CONSUMER_GROUP_ID_FOR_USER", cast=str)


OPENAI_API_KEY = config("OPENAI_API_KEY", cast=Secret)


USERNAME = config("USERNAME", cast=str)
EMAIL = config("EMAIL", cast=str)
FULLNAME = config("FULLNAME", cast=str)
PASSWORD = config("PASSWORD", cast=str)
PHONE = config("PHONE", cast=str)