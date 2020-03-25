from .base import *

DEBUG = TEMPLATE_DEBUG = True

INTERNAL_IPS = ["127.0.0.1", "localhost", "local.rohelp.ro", "192.168.99.100"]

ALLOWED_HOSTS += ["localhost", "192.168.99.100", "local.rohelp.ro"]

AUTH_PASSWORD_VALIDATORS = []

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Add debug toolbar
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar", "django_extensions"]
    MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")

# TODO: read it from env or generate a new one
SECRET_KEY = "https://uploads.skyhighnetworks.com/wp-content/uploads/2015/08/06195203/Bart-Chalkboard-for-Blog-Post.png"

# EMAIL_BACKEND = "django.core.mail.backesnds.console.EmailBackend"

