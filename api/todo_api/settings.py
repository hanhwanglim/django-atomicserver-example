import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-m8ba2r-b50$wtaqjwd!@j!p08$u$_!bv)zk)*28%l37%75bq@("

DEBUG = True

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "tasks",
]

# Conditionally add the 'atomicserver' app, typically only for CI/testing environments.
# This app provides atomic request handling for E2E tests.
# IMPORTANT: Do not add 'atomicserver' to INSTALLED_APPS in production!
if os.environ.get("CI") == "true":
    INSTALLED_APPS.append("atomicserver")

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]


ROOT_URLCONF = "todo_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "todo_api.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # Uses SQLite for simplicity in this example, but can be any other database
        # that supports transactions, i.e. Postgres, MySQL, etc.
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATIC_URL = "static/"
