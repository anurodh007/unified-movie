"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

try:
    from config.env import env
    settings_module = env('DJANGO_SETTINGS_MODULE', default='config.settings')
except (ImportError, NameError):
    settings_module = 'config.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_asgi_application()
