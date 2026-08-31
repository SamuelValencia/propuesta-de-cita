"""
Configuración del proyecto "Propuesta de Cita".

Variables de entorno soportadas (ver .env.example):
    SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL,
    RESEND_API_KEY, DEFAULT_FROM_EMAIL, ADMIN_NOTIFICATION_EMAIL,
    ZONA_HORARIA
"""

import datetime
from pathlib import Path
import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------
# Seguridad / entorno
# --------------------------------------------------------------------------
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-cambia-esta-clave-en-produccion",
)
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

# --------------------------------------------------------------------------
# Apps
# --------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap5",
    "propuesta",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "citaproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "propuesta.context_processors.pasos_progreso",
            ],
        },
    },
]

WSGI_APPLICATION = "citaproject.wsgi.application"

# --------------------------------------------------------------------------
# Base de datos
# Local: SQLite por defecto. Producción: define DATABASE_URL
# (ej. la que entrega Supabase) y se usa Postgres automáticamente.
# --------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL", default="") or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------
# Internacionalización
# --------------------------------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = config("ZONA_HORARIA", default="America/Guayaquil")
USE_I18N = True
USE_TZ = True

# --------------------------------------------------------------------------
# Archivos estáticos (servidos por WhiteNoise en producción)
# --------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# Crispy forms (Bootstrap 5)
# --------------------------------------------------------------------------
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --------------------------------------------------------------------------
# Correo — Resend vía su API HTTP (Render bloquea el tráfico SMTP saliente
# en el plan Free, así que no se usa el backend de correo de Django).
# --------------------------------------------------------------------------
RESEND_API_KEY = config("RESEND_API_KEY", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="Propuesta de Cita <onboarding@resend.dev>")
# Si además del correo a la invitada quieres una copia/alerta interna:
ADMIN_NOTIFICATION_EMAIL = config("ADMIN_NOTIFICATION_EMAIL", default="")

# --------------------------------------------------------------------------
# Reglas del formulario de fecha (parametrizable sin tocar el código)
# --------------------------------------------------------------------------
FECHA_LIMITE = config(
    "FECHA_LIMITE",
    default="2026-09-06",
    cast=lambda v: datetime.date.fromisoformat(v),
)
HORA_MINIMA_ENTRE_SEMANA = config("HORA_MINIMA_ENTRE_SEMANA", default="19:00")

# --------------------------------------------------------------------------
# WhatsApp (link "Escríbeme" en la pantalla final y el correo de confirmación)
# --------------------------------------------------------------------------
WHATSAPP_NUMERO = config("WHATSAPP_NUMERO", default="")

LOGIN_URL = "propuesta:login"
LOGIN_REDIRECT_URL = "propuesta:inicio"
