# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields
import django.db.models.deletion
import service_directory.api.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS citext;",
            reverse_sql="DROP EXTENSION IF EXISTS citext"
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', service_directory.api.models.CaseInsensitiveTextField(unique=True, max_length=50)),
                ('show_on_home_page', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', service_directory.api.models.CaseInsensitiveTextField(unique=True, max_length=100)),
                ('iso_code', service_directory.api.models.CaseInsensitiveTextField(unique=True, max_length=3)),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', service_directory.api.models.CaseInsensitiveTextField(unique=True, max_length=50)),
                ('show_on_home_page', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='KeywordCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.ForeignKey(to='api.Category', on_delete=django.db.models.deletion.PROTECT)),
                ('keyword', models.ForeignKey(to='api.Keyword', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'verbose_name_plural': 'keyword categories',
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('about', models.CharField(max_length=500, blank=True)),
                ('address', models.CharField(max_length=500, blank=True)),
                ('telephone', models.CharField(max_length=50, blank=True)),
                ('emergency_telephone', models.CharField(max_length=50, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('web', models.URLField(blank=True)),
                ('verified_as', models.CharField(max_length=100, blank=True)),
                ('age_range_min', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('age_range_max', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('opening_hours', models.CharField(max_length=50, blank=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('facility_code', models.CharField(max_length=50, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganisationCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.ForeignKey(to='api.Category', on_delete=django.db.models.deletion.PROTECT)),
                ('organisation', models.ForeignKey(to='api.Organisation', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'verbose_name_plural': 'organisation categories',
            },
        ),
        migrations.CreateModel(
            name='OrganisationIncorrectInformationReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reported_at', models.DateTimeField(auto_now_add=True)),
                ('contact_details', models.NullBooleanField()),
                ('address', models.NullBooleanField()),
                ('trading_hours', models.NullBooleanField()),
                ('other', models.NullBooleanField()),
                ('other_detail', models.CharField(max_length=500, blank=True)),
                ('organisation', models.ForeignKey(to='api.Organisation')),
            ],
            options={
                'verbose_name_plural': 'Organisations - Incorrect Information Reports',
            },
        ),
        migrations.CreateModel(
            name='OrganisationKeyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.ForeignKey(to='api.Keyword', on_delete=django.db.models.deletion.PROTECT)),
                ('organisation', models.ForeignKey(to='api.Organisation', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'verbose_name_plural': 'organisation keywords',
            },
        ),
        migrations.CreateModel(
            name='OrganisationRating',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rated_at', models.DateTimeField(auto_now_add=True)),
                ('rating', models.CharField(max_length=10, choices=[('poor', 'Poor'), ('average', 'Average'), ('good', 'Good')])),
                ('organisation', models.ForeignKey(to='api.Organisation')),
            ],
            options={
                'verbose_name_plural': 'Organisations - Ratings',
            },
        ),
        migrations.AddField(
            model_name='organisation',
            name='categories',
            field=models.ManyToManyField(to='api.Category', through='api.OrganisationCategory'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='country',
            field=models.ForeignKey(to='api.Country', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='organisation',
            name='keywords',
            field=models.ManyToManyField(to='api.Keyword', through='api.OrganisationKeyword'),
        ),
        migrations.AddField(
            model_name='keyword',
            name='categories',
            field=models.ManyToManyField(to='api.Category', through='api.KeywordCategory'),
        ),
        migrations.AlterUniqueTogether(
            name='organisationkeyword',
            unique_together=set([('organisation', 'keyword')]),
        ),
        migrations.AlterUniqueTogether(
            name='organisationcategory',
            unique_together=set([('organisation', 'category')]),
        ),
        migrations.AlterUniqueTogether(
            name='keywordcategory',
            unique_together=set([('keyword', 'category')]),
        ),
    ]
