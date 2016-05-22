#!/usr/bin/env python
# encoding: utf-8

import markdown2
import string

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Blog, BlogEntry, Comments


DEFAULT_AVATAR_URL = u'blogger.png'
DEFAULT_HEADER_URL = u'Green_Blog.jpg'


class AddBlogForm(forms.Form):
    name = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AddBlogForm, self).__init__(*args, **kwargs)

    def clean(self):
        # check if bloger has blog
        if Blog.objects.filter(bloger=self.request.user).exists():
            raise forms.ValidationError(u'Ten użytkownik prowadzi już bloga.')
        return super(AddBlogForm, self).clean()

    def save(self):
        name = self.cleaned_data.get('name')

        # create slug
        words_in_name_list = name.split(' ')
        slug = '_'.join(words_in_name_list[:4])

        # if slug exists, create slug with last free number
        if Blog.objects.filter(slug=slug).exists():
            slug_base = slug.rstrip('0123456789')
            pattern = r'^' + slug_base + r'[0-9]+$'
            last_slug_blog = Blog.objects.filter(slug__iregex=pattern)\
                .order_by('slug').last()
            if last_slug_blog:
                last_slug_number = int(last_slug_blog.slug.replace(
                    slug_base, ''))
                slug = slug_base + str(last_slug_number + 1)
            else:
                slug = slug_base + '1'

        for char in slug:
            if char not in string.ascii_letters+'_':
                slug = slug.replace(char, '')

        bloger = self.request.user
        blog = Blog.objects.create(
            name=name, slug=slug, bloger=bloger,
            avatar_url=DEFAULT_AVATAR_URL,
            headline_picture_url=DEFAULT_HEADER_URL)
        blog.save()

        return blog


class ConfigureBlogForm(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ['name', 'description', 'avatar_url', 'headline_picture_url']


class AddBlogEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.blog = kwargs.pop('blog', None)
        super(AddBlogEntryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BlogEntry
        fields = ['title', 'summary', 'first_picture_url', 'markdown_body',
                  'comments_allowed', 'pictures_json']

    def save(self, commit=True):
        title = self.cleaned_data['title']
        words_in_name_list = title.split(' ')
        slug = '_'.join(words_in_name_list[:4])
        slug = slug.replace('.', '')
        for char in slug:
            if char not in string.ascii_letters+'_':
                slug = slug.replace(char, '')

        if BlogEntry.objects.filter(slug=slug).exists():
            slug_base = slug.rstrip('0123456789')
            pattern = r'^' + slug_base + r'[0-9]+$'
            last_slug_blog = Blog.objects.filter(slug__iregex=pattern)\
                .order_by('slug').last()
            if last_slug_blog:
                last_slug_number = int(last_slug_blog.slug.replace(
                    slug_base, ''))
                slug = slug_base + str(last_slug_number + 1)
            else:
                slug = slug_base + '1'

        summary = self.cleaned_data['summary']
        first_picture_url = self.cleaned_data['first_picture_url']
        pictures_json = self.cleaned_data['pictures_json']

        markdown_body = self.cleaned_data['markdown_body']
        body = markdown2.markdown(markdown_body)

        comments_allowed = self.cleaned_data['comments_allowed']

        blog_entry = BlogEntry.objects.create(
            blog=self.blog, title=title, slug=slug, summary=summary,
            first_picture_url=first_picture_url, body=body,
            comments_allowed=comments_allowed, pictures_json=pictures_json,
            markdown_body=markdown_body,
            )
        return blog_entry


class EditBlogEntryForm(forms.ModelForm):
    class Meta:
        model = BlogEntry
        fields = ['title', 'summary', 'first_picture_url', 'markdown_body',
                  'comments_allowed', 'pictures_json']

    def save(self, *args, **kwargs):
        blog_entry = self.instance
        blog_entry.title = self.cleaned_data['title']
        blog_entry.summary = self.cleaned_data['summary']
        blog_entry.first_picture_url = self.cleaned_data['first_picture_url']
        blog_entry.pictures_json = self.cleaned_data['pictures_json']

        blog_entry.updated_at = timezone.now()
        blog_entry.markdown_body = self.cleaned_data['markdown_body']
        blog_entry.body = markdown2.markdown(blog_entry.markdown_body)

        blog_entry.comments_allowed = self.cleaned_data['comments_allowed']
        blog_entry.save()
        return blog_entry


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.blog_entry = kwargs.pop('blog_entry', None)
        self.user = kwargs.pop('user', None)
        super(CommentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Comments
        fields = ['body']

    def save(self, *args, **kwargs):
        body = self.cleaned_data['body']
        if self.user.is_anonymous():
            author = u'Gość'
        else:
            author = self.user.username
        comment = Comments.objects.create(blog_entry=self.blog_entry,
                                          author=author, body=body)
        comment.save()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
