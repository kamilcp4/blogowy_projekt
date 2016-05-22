# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('slug', models.CharField(unique=True, max_length=200)),
                ('avatar_url', models.URLField()),
                ('headline_picture_url', models.URLField()),
                ('description', models.TextField(null=True, blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('status', models.IntegerField(default=0)),
                ('is_recommended', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('bloger', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BlogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('slug', models.CharField(unique=True, max_length=200)),
                ('summary', models.CharField(max_length=400)),
                ('first_picture_url', models.URLField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_recommended', models.BooleanField(default=False)),
                ('status', models.IntegerField(default=0)),
                ('comments_allowed', models.BooleanField(default=True)),
                ('blog', models.ForeignKey(to='blog.Blog')),
            ],
            options={
                'verbose_name_plural': 'Blog Entries',
            },
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=0)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('blog_entry', models.ForeignKey(to='blog.BlogEntry')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, null=True, blank=True)),
                ('photo', models.ImageField(upload_to=b'/static/photos/')),
                ('blog_entry', models.ForeignKey(to='blog.BlogEntry')),
            ],
        ),
    ]
