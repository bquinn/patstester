# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20160329_1700'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patsevent',
            old_name='entity_type',
            new_name='subscription_type'
        ),
    ]
