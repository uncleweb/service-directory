# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_organisation_location'),
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('categories', models.ManyToManyField(to='api.Category')),
            ],
            options={
                'verbose_name_plural': 'keywords',
            },
        ),
        migrations.RemoveField(
            model_name='service',
            name='keywords',
        ),
        migrations.AddField(
            model_name='service',
            name='keywords',
            field=models.ManyToManyField(to='api.Keyword'),
        ),
    ]
