#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import, division

from .enums import moderation_states, blog_entry_states
from .models import Blog


class UserPermissions(object):
    def __init__(self, user, blog=None, blog_entry=None):
        self.user = user
        self.blog = blog
        self.blog_entry = blog_entry

        if blog:
            self.is_blog_owner = self.get_blog_owner_permission()
            self.can_show_main_blog_page = self.get_show_main_blog_page_permission()
            self.can_show_blog_entry = self.get_show_blog_entry_permission()
            self.can_add_entry = self.get_add_entry_permission()
            self.can_configure_blog = self.get_configure_permission()

    def get_blog_owner_permission(self):
        return self.blog.bloger.id == self.user.id

    def get_show_main_blog_page_permission(self):
        # Can show main blog page
        if (not self.blog.is_active) or \
                (self.blog.status != moderation_states.accepted and not
                 self.is_blog_owner):
            return False
        return True

    def get_show_blog_entry_permission(self):
        # Can show blog entry
        if (not self.blog_entry) or (not self.can_show_main_blog_page):
            return False
        else:
            if (self.blog_entry.status != blog_entry_states.published or
                    not self.blog_entry.is_active) and not self.is_blog_owner:
                return False
            return True

    def get_add_entry_permission(self):
        if self.blog.status == moderation_states.rejected \
           or (not self.is_blog_owner) or (not self.blog.is_active):
            return False
        return True

    def get_configure_permission(self):
        return self.blog.is_active and self.is_blog_owner

    def get_create_blog_permission(self):
        if self.user.is_authenticated() \
                and not Blog.objects.filter(bloger_id=self.user.id).exists():
            return True
        return False


def get_key(item):
    return item[0].lower()