from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()

DATABASE_URL = config("DATABASE_URL", cast=Secret)
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)

BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)

KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str)
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

OPENAI_API_KEY = config("OPENAI_API_KEY", cast=Secret)


USERNAME = config("USERNAME", cast=str)
EMAIL = config("EMAIL", cast=str)
FULLNAME = config("FULLNAME", cast=str)
PASSWORD = config("PASSWORD", cast=str)
PHONE = config("PHONE", cast=str)
FIRST_NAME = config("FIRSTNAME", cast=str)
LAST_NAME = config("LASTNAME", cast=str)