# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='emergency_telephone',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AddField(
            model_name='organisation',
            name='facility_code',
            field=models.CharField(max_length=50, blank=True),
        ),
    ]
