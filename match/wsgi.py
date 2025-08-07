import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'match.settings')

application = get_wsgi_application()

# Use the STATIC_ROOT path defined in settings.py
application = WhiteNoise(application, root=settings.STATIC_ROOT)