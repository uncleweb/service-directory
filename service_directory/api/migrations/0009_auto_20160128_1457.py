# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import service_directory.api.models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20160127_1232'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS citext;",
            reverse_sql="DROP EXTENSION IF EXISTS citext"
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=service_directory.api.models.CaseInsensitiveTextField(unique=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='country',
            name='iso_code',
            field=service_directory.api.models.CaseInsensitiveTextField(unique=True, max_length=3),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=service_directory.api.models.CaseInsensitiveTextField(unique=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='keyword',
            name='name',
            field=service_directory.api.models.CaseInsensitiveTextField(unique=True, max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='countryarea',
            unique_together=set([('name', 'level', 'country')]),
        ),
    ]
