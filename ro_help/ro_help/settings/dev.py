from .base import *

INTERNAL_IPS = ["127.0.0.1", "localhost", "local.rohelp.ro", "192.168.99.100"]

ALLOWED_HOSTS += ["localhost", "192.168.99.100", "local.rohelp.ro", "dev.rohelp.ro"]

AUTH_PASSWORD_VALIDATORS = []

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# No Google/Facebook trackers in the dev env
ANALYTICS_ENABLED = False

# Add debug toolbar
if DEBUG and env("ENABLE_DEBUG_TOOLBAR"):
    INSTALLED_APPS += ["debug_toolbar", "django_extensions"]
    MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    }

if not DEBUG:
    MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

    STATIC_ROOT = os.path.join(BASE_DIR, "../", "static")
    STATICFILES_DIRS = []
