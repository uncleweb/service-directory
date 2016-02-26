# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_serviceincorrectinformationreport'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rated_at', models.DateTimeField(auto_now_add=True)),
                ('rating', models.CharField(max_length=10, choices=[('poor', 'Poor'), ('average', 'Average'), ('good', 'Good')])),
                ('service', models.ForeignKey(to='api.Service')),
            ],
            options={
                'verbose_name_plural': 'Services - Ratings',
            },
        ),
        migrations.AlterModelOptions(
            name='serviceincorrectinformationreport',
            options={'verbose_name_plural': 'Services - Incorrect Information Reports'},
        ),
    ]
