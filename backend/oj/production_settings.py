from utils.shortcuts import get_env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': get_env("POSTGRES_HOST", "oj-postgres"),
        'PORT': get_env("POSTGRES_PORT", "5432"),
        'NAME': get_env("POSTGRES_DB"),
        'USER': get_env("POSTGRES_USER"),
        'PASSWORD': get_env("POSTGRES_PASSWORD")
    }
}

REDIS_CONF = {
    "host": get_env("REDIS_HOST", "oj-redis"),
    "port": get_env("REDIS_PORT", "6379")
}

DEBUG = False

ALLOWED_HOSTS = ['*']

DATA_DIR = "/data"

CSRF_TRUSTED_ORIGINS = ["https://coding.riibotics.io", "http://coding.riibotics.io"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

