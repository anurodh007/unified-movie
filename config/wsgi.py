"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from whitenoise import WhiteNoise

try:
    from config.env import env
    settings_module = env('DJANGO_SETTINGS_MODULE', default='config.settings')
except (ImportError, NameError):
    settings_module = 'config.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()

# Forces Whitenoise to handle media files.
application = WhiteNoise(application, root=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/'))
application.add_files(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media/'), prefix='media/')