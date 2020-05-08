from django.conf import settings


def hub_settings(context):
    return {
        "DEBUG": settings.DEBUG,
        "ANALYTICS_ENABLED": settings.ANALYTICS_ENABLED,
    }
