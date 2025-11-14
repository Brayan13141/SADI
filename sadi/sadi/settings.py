import os
from pathlib import Path
from decouple import config
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

SITE_NAME = "SADI"
DOMAIN = "sadi.surguanajuato.tecnm.mx"
# Dirección base para los enlaces en correos
DEFAULT_FROM_EMAIL = f"no-reply@{DOMAIN}"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(",")

# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # REST_FRAMEWORK
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    # Django AllAuth
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Third party
    "simple_history",
    # Local apps
    "usuarios",
    "departamentos",
    "programas",
    "objetivos",
    "proyectos",
    "metas",
    "actividades",
    "riesgos",
    "reportes",
    "mcp",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

ROOT_URLCONF = "sadi.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.estado_sistema",  # CONTEXTO GLOBAL ESTADO SISTEMA
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
    }
}

JAZZMIN_SETTINGS = {
    "site_title": "SADI Admin",
    "site_header": "Panel de Administración SADI",
    "welcome_sign": "Bienvenido al sistema institucional",
    "show_sidebar": True,
    "search_model": "usuarios.Usuario",
    "hide_models": ["auth.Group"],
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "navbar": "navbar-dark navbar-primary",
    "sidebar": "sidebar-dark-primary",
    "brand_colour": "navbar-primary",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "debug.log"),
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "mcp": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

MCP_CONFIG = {
    "MODEL_NAME": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # Nombre completo del modelo
    "MODEL_PATH": "/home/sadi/.cache/huggingface/hub/",
    "MAX_LENGTH": 512,
    "TEMPERATURE": 0.7,
    "USE_GPU": torch.cuda.is_available(),
}


def get_llm_model():
    """Función para cargar el modelo de lenguaje (mantener al final del archivo)"""
    try:
        model_name = MCP_CONFIG["MODEL_NAME"]
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if MCP_CONFIG["USE_GPU"] else torch.float32,
            device_map="auto" if MCP_CONFIG["USE_GPU"] else None,
        )
        return model, tokenizer
    except Exception as e:
        print(f"Error cargando el modelo: {e}")
        return None, None


AUTH_USER_MODEL = "usuarios.Usuario"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

# Configuración del backend de correo electrónico para desarrollo
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# Configuración del backend de correo electrónico para producción
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config(
    "EMAIL_HOST_PASSWORD"
)  # Se genera en https://myaccount.google.com/apppasswords
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# CONFIGURACIONES PARA DJANGO ALLAUTH
SITE_ID = 1
ACCOUNT_LOGIN_METHODS = {"username", "email"}  # Permite usuario o email
ACCOUNT_UNIQUE_EMAIL = True  # Evita correos duplicados
ACCOUNT_SIGNUP_FIELDS = [
    "username*",
    "email*",
    "password1*",
    "password2*",
]  # Campos obligatorios

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "dashboard"
ACCOUNT_LOGOUT_REDIRECT_URL = "/accounts/login/"

LANGUAGE_CODE = "es-MX"

WSGI_APPLICATION = "sadi.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
# CONFIGURACION PARA EL LENGUAJE Y LA ZONA HORARIA
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Configuración de archivos multimedia
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Configuraciones de seguridad para ngrok
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Configuración CSRF para ngrok
CSRF_TRUSTED_ORIGINS = [
    "https://a1835a660220.ngrok-free.app",
    "https://*.ngrok-free.app",
    "https://*.ngrok.io",
    "http://192.168.0.161",
    "http://localhost",
    "http://127.0.0.1",
]

USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
