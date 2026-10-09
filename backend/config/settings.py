"""
Configuración de Django para DeliverTrack.

Las variables sensibles (clave secreta, base de datos, hosts) se leen del
entorno; ver `.env.example`. El repositorio nunca contiene claves reales.
"""
import os
import warnings
from datetime import timedelta
from pathlib import Path


def env(nombre: str, por_defecto: str = "") -> str:
    """Lee una variable de entorno con valor por defecto."""
    return os.environ.get(nombre, por_defecto)


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env(
    "DJANGO_SECRET_KEY", "clave-solo-para-desarrollo-local-cambiar"
)
DEBUG = env("DEBUG", "1") == "1"

if not DEBUG and SECRET_KEY.startswith("clave-solo-para-desarrollo"):
    raise RuntimeError(
        "Seguridad: en producción debe definirse DJANGO_SECRET_KEY en el entorno."
    )

ALLOWED_HOSTS = [
    h.strip() for h in env("ALLOWED_HOSTS", "*").split(",") if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceros
    "rest_framework",
    "corsheaders",
    # Aplicaciones del proyecto (organizadas por responsabilidad)
    "apps.accounts",
    "apps.operations",
    "apps.analytics",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# --- Base de datos -------------------------------------------------------
# Desarrollo: SQLite. Producción/nube: DATABASE_URL (por ejemplo PostgreSQL).
if env("DATABASE_URL"):
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            env("DATABASE_URL"), conn_max_age=600
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_USER_MODEL = "accounts.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- CORS ----------------------------------------------------------------
# En desarrollo se permite todo; en producción se lista el origen del frontend.
CORS_ALLOWED_ORIGINS = [
    o.strip() for o in env("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()
]
if DEBUG and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOW_ALL_ORIGINS = True

LANGUAGE_CODE = "es"
TIME_ZONE = env("TIME_ZONE", "America/Managua")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Regla de automatización (detección de entregas en riesgo) -----------
# Margen en minutos: si a una entrega activa le quedan RIESGO_MINUTOS o menos
# para su hora límite, se clasifica EN_RIESGO; si la hora límite ya pasó,
# RETRASADA. Ver apps/operations/services/risk.py para los límites completos.
RIESGO_MINUTOS = int(env("RIESGO_MINUTOS", "30"))

# En producción lo correcto es un planificador (cron) que ejecute
# `python manage.py evaluar_riesgos` cada minuto. Para la demo del MVP,
# el tablero también dispara la evaluación al consultar el resumen.
EVALUAR_RIESGO_AL_CONSULTAR = env("EVALUAR_RIESGO_AL_CONSULTAR", "1") == "1"
