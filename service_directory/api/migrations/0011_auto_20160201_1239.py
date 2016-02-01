# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20160201_1157'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='countryarea',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='countryarea',
            name='country',
        ),
        migrations.RemoveField(
            model_name='organisation',
            name='areas',
        ),
        migrations.DeleteModel(
            name='CountryArea',
        ),
    ]
