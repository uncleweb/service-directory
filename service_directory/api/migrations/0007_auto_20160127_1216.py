# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20160126_0755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organisation',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default='SRID=4326;POINT (0.0 0.0)', srid=4326),
        ),
    ]
