# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20151220_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogentry',
            name='markdown_body',
            field=models.TextField(default=datetime.datetime(2016, 1, 3, 13, 36, 25, 669324, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
