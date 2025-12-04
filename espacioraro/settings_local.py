from .settings import *  # Importa todo lo de producción

# ============================================================
# CONFIGURACIÓN LOCAL PARA DESARROLLO
# ============================================================

DEBUG = True

# BD LOCAL SQLITE (no toca tu AWS MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}

# Hosts permitidos localmente
ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]

# Evita enviar correos reales durante las pruebas
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Archivos estáticos: usa la carpeta local
STATICFILES_DIRS = [BASE_DIR / "static"]

# Desactiva CSRF en pruebas locales si lo necesitas
# (solo déjalo así si lo requieres para formularios en test)
# CSRF_TRUSTED_ORIGINS = ["http://localhost*", "http://127.0.0.1*"]
