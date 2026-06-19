from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import dj_database_url
from django.utils.translation import gettext_lazy as _

# ─── تحميل .env ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ .env loaded from: {env_path}")
else:
    print(f"⚠️ .env not found at: {env_path}")

print(f"🔑 GROQ_API_KEY: {os.environ.get('GROQ_API_KEY', 'NOT FOUND')[:15]}...")
print(f"🔑 GEMINI_API_KEY: {os.environ.get('GEMINI_API_KEY', 'NOT FOUND')[:15]}...")

# ─── Security ────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,veridz.onrender.com,veri-dz-website.onrender.com').split(',')

# ─── Applications ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'cloudinary',
    'cloudinary_storage',
    # Local - accounts MUST come before admin
    'accounts',
    'core',
    'news',
    'factcheck',
    'dashboard',
    'publications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.LanguageMiddleware',  # Language middleware
]

ROOT_URLCONF = 'news_verifier.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.language_context',  # Language context
            ],
        },
    },
]

WSGI_APPLICATION = 'news_verifier.wsgi.application'

# ─── Database ─────────────────────────────────────────────────────────────
ON_RENDER = os.environ.get('RENDER', False)

if ON_RENDER:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                ssl_require=True,
            )
        }
        print(f"✅ Production: Using PostgreSQL database")
    else:
        raise ValueError("DATABASE_URL environment variable is not set on Render!")
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("✅ Development: Using SQLite database")

# ─── Auth ────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Localisation ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'ar-dz'
TIME_ZONE = 'Africa/Algiers'
USE_I18N = True
USE_TZ = True

# اللغات المدعومة
LANGUAGES = [
    ('ar', _('العربية')),
    ('fr', _('Français')),
    ('en', _('English')),
]

# ─── Static files ─────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─── Cloudinary – Media files ─────────────────────────────────────────────────
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY':    os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

if ON_RENDER and not DEBUG:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    MEDIA_ROOT = BASE_DIR / 'media'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

MEDIA_URL = '/media/'

# ─── Miscellaneous ────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# ─── APIs ─────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# ─── Production security extras ──────────────────────────────────────────────
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True