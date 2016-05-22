# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_comments_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='avatar_url',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='blog',
            name='headline_picture_url',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='blogentry',
            name='first_picture_url',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
