# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20160128_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='country',
            field=models.ForeignKey(to='api.Country', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
