"""
Django settings for patstester project - production instance.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/
"""

from patstester.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['apitester.pats.org.uk']

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'patstester', # 'get_env_variable('PATSTESTER_DB_NAME'),
    'USER': 'patstester', # get_env_variable('PATSTESTER_DB_USER'),
    'PASSWORD': 'p4tsT3ster', # get_env_variable('PATSTESTER_DB_PASSWORD'),
    'HOST': 'patstester-db.cbnfejxauezt.eu-west-1.rds.amazonaws.com', # get_env_variable('PATSTESTEr_DB_HOST'),
    'PORT': '5432', # get_env_variable('BUBBLYGUIDE_DB_PORT')
  }
}

SECRET_KEY = 'ao(i7!wdcnc*%^oex^hir9cazxu_hbq=20d$8iasdfs&&!s0t^h=($'
