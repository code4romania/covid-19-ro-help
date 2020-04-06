from .base import *

DEBUG = TEMPLATE_DEBUG = False

SECRET_KEY = env("SECRET_KEY")

MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_ROOT = os.path.join(BASE_DIR, "../", "static")
STATICFILES_DIRS = []
