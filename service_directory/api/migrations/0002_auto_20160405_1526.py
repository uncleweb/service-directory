# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keywordcategory',
            name='keyword',
            field=models.ForeignKey(to='api.Keyword'),
        ),
        migrations.AlterField(
            model_name='organisationcategory',
            name='organisation',
            field=models.ForeignKey(to='api.Organisation'),
        ),
        migrations.AlterField(
            model_name='organisationkeyword',
            name='organisation',
            field=models.ForeignKey(to='api.Organisation'),
        ),
    ]
