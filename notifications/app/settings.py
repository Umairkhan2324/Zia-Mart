from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()



KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str)

BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)

KAFKA_CONSUMER_GROUP_ID_FOR_USER = config("KAFKA_CONSUMER_GROUP_ID_FOR_USER", cast=str)
GOOGLE_API_KEY = config("GOOGLE_API_KEY", cast=str)

AUTH_SERVER_URL = config("AUTH_SERVER_URL", cast=str)


SMTP_HOST = config("SMTP_HOST", cast=str)
SMTP_USER = config("SMTP_USER", cast=str)
SMTP_PASSWORD = config("SMTP_PASSWORD", cast=str)
EMAILS_FROM_EMAIL = config("EMAILS_FROM_EMAIL", cast=str)
SMTP_TLS = config("SMTP_TLS", cast=str)
SMTP_SSL = config("SMTP_SSL", cast=str)
SMTP_PORT = config("SMTP_PORT", cast=str)
EMAILS_FROM_NAME = config("EMAILS_FROM_NAME", cast=str)
emails_enabled = True
EMAILS_FROM_EMAIL = "asadsher2324@gmail.com"