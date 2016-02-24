# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20160201_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceIncorrectInformationReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reported_at', models.DateTimeField(auto_now_add=True)),
                ('contact_details', models.NullBooleanField()),
                ('address', models.NullBooleanField()),
                ('trading_hours', models.NullBooleanField()),
                ('other', models.NullBooleanField()),
                ('other_detail', models.CharField(max_length=500, blank=True)),
                ('service', models.ForeignKey(to='api.Service')),
            ],
        ),
    ]
