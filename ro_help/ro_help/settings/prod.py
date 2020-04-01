from .base import *

DEBUG = TEMPLATE_DEBUG = False

SECRET_KEY = env("SECRET_KEY")

MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_ROOT = os.path.join(BASE_DIR, "../", "static")
