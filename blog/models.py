#!/usr/bin/env python
# encoding: utf-8

from jsonfield.fields import JSONField

from django.contrib.auth.models import User
from django.db import models

from .enums import blog_entry_states, moderation_states


class Blog(models.Model):
    name = models.CharField(max_length=200)
    bloger = models.ForeignKey(User)
    slug = models.CharField(max_length=200, unique=True)

    avatar_url = models.CharField(max_length=200)
    headline_picture_url = models.CharField(max_length=200)

    description = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    status = models.IntegerField(default=moderation_states.private)
    is_recommended = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name


class BlogEntry(models.Model):
    blog = models.ForeignKey(Blog)

    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)
    summary = models.CharField(max_length=1000)
    first_picture_url = models.CharField(null=True, blank=True, max_length=200)
    pictures_json = JSONField(default=[], null=True, blank=True)

    body = models.TextField()
    markdown_body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_recommended = models.BooleanField(default=False)
    status = models.IntegerField(default=blog_entry_states.published)

    comments_allowed = models.BooleanField(default=True)
    visited = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Blog Entries'

    def __unicode__(self):
        return self.title


class Photo(models.Model):
    picture = models.ImageField(upload_to='/var/www/blog/photos/')

    def get_name(self):
        return str(self.picture).split('/')[-1]

    def __unicode__(self):
        return self.get_name()


class Comments(models.Model):
    blog_entry = models.ForeignKey(BlogEntry)
    author = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    status = models.IntegerField(default=blog_entry_states.published)
