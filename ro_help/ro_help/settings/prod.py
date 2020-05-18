from .base import *

# Fail-safe: make sure that we never run DEBUG in production
DEBUG = TEMPLATE_DEBUG = False

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = ["rohelp.ro", "www.rohelp.ro"]

MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_ROOT = os.path.join(BASE_DIR, "../", "static")
STATICFILES_DIRS = []
