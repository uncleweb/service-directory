# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20160229_1225'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('name', 'organisation')]),
        ),
    ]
