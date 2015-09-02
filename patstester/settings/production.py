"""
Django settings for patstester project - production instance.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/
"""

from patstester.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['apitester.pats.org.uk']

TEMPLATES[0]['DIRS'] = [ '/var/www/apitester.pats.org.uk/patstester/templates/' ]

SECRET_KEY = 'ao(i7!wdcnc*%^oex^hir9cazxu_hbq=20d$8iasdfs&&!s0t^h=($'
