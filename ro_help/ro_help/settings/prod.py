from .base import *

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = TEMPLATE_DEBUG = False

SECRET_KEY = env("SECRET_KEY")

MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_ROOT = os.path.join(BASE_DIR, "../", "static")
STATICFILES_DIRS = []

sentry_sdk.init(
    dsn="https://fafd029cf71346c1b9c44397e6634b47@o375441.ingest.sentry.io/5194891",
    integrations=[DjangoIntegration()],
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)
