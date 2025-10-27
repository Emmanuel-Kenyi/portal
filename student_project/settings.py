import os
from pathlib import Path
from dotenv import load_dotenv
from decouple import config
import dj_database_url

# -----------------------------
# BASE DIRECTORY
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env variables
load_dotenv(BASE_DIR / ".env")

# -----------------------------
# SECURITY
# -----------------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-placeholder')
DEBUG = config('DEBUG', default=False, cast=bool)

# ALLOWED_HOSTS - Use Render's automatic hostname or environment variable
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, '127.0.0.1', 'localhost']
else:
    # Fallback to config or default
    ALLOWED_HOSTS = [h.strip() for h in config(
        'ALLOWED_HOSTS',
        default='127.0.0.1,localhost'
    ).split(',')]

# -----------------------------
# SUPABASE
# -----------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# -----------------------------
# INSTALLED APPS
# -----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clubs',
    'users',
]

# -----------------------------
# MIDDLEWARE
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'student_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'student_project.wsgi.application'

# -----------------------------
# DATABASE
# -----------------------------
# Use SQLite for local/dev, PostgreSQL in production if DATABASE_URL is provided
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------
# INTERNATIONALIZATION
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# STATIC FILES
# -----------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]        # Dev
STATIC_ROOT = BASE_DIR / "staticfiles"          # Production

# -----------------------------
# MEDIA FILES
# -----------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------
# DEFAULT PK
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------
# LOGIN / LOGOUT
# -----------------------------
LOGIN_REDIRECT_URL = '/users/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'