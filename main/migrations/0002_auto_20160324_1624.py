# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patsevent',
            name='entity_type',
            field=models.CharField(max_length=30, verbose_name='entity type', blank=True),
        ),
        migrations.AlterField(
            model_name='patsevent',
            name='subscription_type',
            field=models.CharField(max_length=30, verbose_name='entity type', blank=True),
        ),
    ]
