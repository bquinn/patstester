# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20160324_1624'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patsevent',
            old_name='subscription_type',
            new_name='event_type'
        ),
    ]
