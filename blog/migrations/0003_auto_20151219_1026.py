# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_blogentry_visited'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogentry',
            name='body',
            field=models.TextField(),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='comments',
            name='body',
            field=models.TextField(),
            preserve_default=False,
        ),
    ]
