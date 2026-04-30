# ============================================================
# ADD TO news_verifier/settings.py
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Local apps
    'core',
    'accounts',
    'news',
    'factcheck',
    'dashboard',
    'publications',   # <-- ADD THIS
]

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Media files (uploaded images & videos)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


# ============================================================
# news_verifier/urls.py  (FULL FILE)
# ============================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('news/', include('news.urls')),
    path('fact-check/', include('factcheck.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('publications/', include('publications.urls')),   # <-- ADD THIS
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
