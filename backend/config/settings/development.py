"""
Development settings for Skill Swap.
Extends base settings with dev-friendly defaults.
"""

from .base import *  # noqa: F401, F403

# =============================================================================
# DEBUG
# =============================================================================
DEBUG = True

# =============================================================================
# DATABASE — SQLite for local development (no PostgreSQL required)
# Override with PostgreSQL via .env if needed
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}

# =============================================================================
# EMAIL — print to console in development
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# =============================================================================
# CORS — allow all in development
# =============================================================================
CORS_ALLOW_ALL_ORIGINS = True

# =============================================================================
# REST FRAMEWORK — add browsable API renderer in dev
# =============================================================================
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
)

# =============================================================================
# THROTTLE — relaxed rates for development
# =============================================================================
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {  # noqa: F405
    'anon': '100/minute',
    'user': '500/minute',
    'login': '20/minute',
    'register': '20/minute',
}

# =============================================================================
# LOGGING
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
