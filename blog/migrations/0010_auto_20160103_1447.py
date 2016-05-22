# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_blogentry_markdown_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogentry',
            name='summary',
            field=models.CharField(max_length=1000),
        ),
    ]
