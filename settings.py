from pathlib import Path
import os
from dotenv import load_dotenv
import logging
import sys

# =====================
# Cargar variables .env
# =====================
load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s %(asctime)s %(module)s %(message)s",
    stream=sys.stdout,
)

BASE_DIR = Path(__file__).resolve().parent.parent

# =====================
# Seguridad
# =====================

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "espacioraro.cl",
    "www.espacioraro.cl",
]

CSRF_TRUSTED_ORIGINS = [
    "https://espacioraro.cl",
    "https://www.espacioraro.cl",
]

# =====================
# Aplicaciones
# =====================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'espacioraro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'espacioraro.wsgi.application'

# =====================
# Base de datos
# =====================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT", "3306"),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# =====================
# Validación contraseñas
# =====================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]



# =====================
# Internacionalización# =====================

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# =====================
# Archivos Estáticos
# (Correctos para producción con Nginx)
# =====================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"   # carpeta donde collectstatic guarda archivos

STATICFILES_DIRS = [
    BASE_DIR / "static",  # si NO usas carpeta "static", elimina esta línea
]

# =====================
# Archivos Media (imagenes)
# =====================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =====================
# Email SMTP (Gmail)
# =====================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
                
}


# =====================
# Por defecto
# =====================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
