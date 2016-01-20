# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-08 10:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'categories'},
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'verbose_name_plural': 'countries'},
        ),
        migrations.AlterField(
            model_name='organisation',
            name='about',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='address',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='telephone',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='web',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='age_range_max',
            field=models.PositiveSmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='age_range_min',
            field=models.PositiveSmallIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='availability_hours',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='service',
            name='verified_as',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]