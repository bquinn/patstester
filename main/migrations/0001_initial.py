# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PATSEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entity_id', models.CharField(max_length=15, verbose_name='entity ID', blank=True)),
                ('event_date', models.DateTimeField(verbose_name='event date', blank=True)),
                ('entity_type', models.CharField(max_length=15, verbose_name='entity type', blank=True)),
                ('subscription_type', models.CharField(max_length=15, verbose_name='entity type', blank=True)),
                ('major_version', models.CharField(max_length=5, verbose_name='major version', blank=True)),
                ('minor_version', models.CharField(max_length=5, verbose_name='minor version', blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
    ]
