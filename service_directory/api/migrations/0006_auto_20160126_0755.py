# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20160125_1221'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='keyword',
            options={},
        ),
        migrations.AddField(
            model_name='category',
            name='show_on_home_page',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='keyword',
            name='show_on_home_page',
            field=models.BooleanField(default=False),
        ),
    ]
