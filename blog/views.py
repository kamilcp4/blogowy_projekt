#!/usr/bin/env python
# encoding: utf-8

from __future__ import absolute_import

import json
import markdown2

from annoying.decorators import render_to, ajax_request
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect

from .enums import blog_entry_states, moderation_states
from .forms import AddBlogForm, ConfigureBlogForm, EditBlogEntryForm, \
    AddBlogEntryForm, CommentForm, UserForm
from .helpers import UserPermissions, get_key
from .models import Blog, BlogEntry, Photo, Comments

from blogowy_projekt.settings import MAX_BLOGS_ON_PAGE, \
    MAX_BLOG_ENTRIES_ON_PAGE


def logout_page(request):
    logout(request)
    return redirect('/')


def registration(request):
    user_form = UserForm(data=request.POST or None)
    if request.method == 'POST':
        password = request.POST['password']
        repeated_password = request.POST['password_2']
        if password == repeated_password:
            if user_form.is_valid():
                user = user_form.save()
                user.set_password(user.password)
                user.save()
                user = authenticate(username=user.username, password=password)
                login(request, user)
                return redirect('/')
    return redirect('login')


@render_to('statute.html')
def statute(request):
    return {}


@render_to('blogs.html')
def blogs(request):
    # get blog entries
    blog_entries = BlogEntry.objects.only(
        'blog', 'slug', 'title', 'first_picture_url', 'summary',)\
        .filter(is_active=True, status=blog_entry_states.published,
                blog__status=moderation_states.accepted,
                blog__is_active=True).order_by('-created_at')

    # get most popular
    most_popular = BlogEntry.objects.only(
        'blog', 'slug', 'title', 'first_picture_url', 'summary',)\
        .filter(is_active=True, status=blog_entry_states.published,
                blog__status=moderation_states.accepted,
                blog__is_active=True).order_by('-visited')[:3]

    # paginate blogs entries
    page_number = request.GET.get('strona', 1)
    pagination_page = get_paginated_page(blog_entries, MAX_BLOG_ENTRIES_ON_PAGE,
                                         page_number)
    blog_entries = pagination_page.object_list

    # get blogs
    blogs = Blog.objects.only('name', 'slug',)\
        .filter(is_active=True, status=moderation_states.accepted)\
        .order_by('name')

    blogs_data = sorted([(blog.name, blog.slug) for blog in blogs], key=get_key)

    return {
        'blog_entries': blog_entries,
        'pagination_page': pagination_page,
        'blogs_data': json.dumps(blogs_data),
        'max_blogs_on_page': MAX_BLOGS_ON_PAGE,
        'most_popular': most_popular,
    }


@render_to('main_blog_page.html')
def main_blog_page(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)

    user_permissions = UserPermissions(request.user, blog)
    if not user_permissions.can_show_main_blog_page:
        raise Http404()

    blog_entries = BlogEntry.objects.only(
        'first_picture_url', 'summary', 'slug', 'status', 'title')\
        .filter(blog=blog.id).order_by('-created_at')

    if not user_permissions.is_blog_owner:
        blog_entries = blog_entries.filter(status=blog_entry_states.published,
                                           is_active=True)

    # paginate blog entries
    page_number = request.GET.get('strona', 1)
    pagination_page = get_paginated_page(blog_entries, MAX_BLOG_ENTRIES_ON_PAGE,
                                         page_number)
    blog_entries = pagination_page.object_list

    return {
        'blog': blog,
        'blog_entries': blog_entries,
        'pagination_page': pagination_page,
        'moderation_states': moderation_states,
        'blog_entry_states': blog_entry_states,
        'user_permissions': user_permissions,
    }


@render_to('blog_entry.html')
def blog_entry(request, blog_slug, blog_entry_id, blog_entry_slug):
    blog_entry = get_object_or_404(BlogEntry, id=blog_entry_id)

    if blog_entry.slug != blog_entry_slug \
            or blog_entry.blog.slug != blog_slug:
        return redirect('blog_entry', blog_slug=blog_entry.blog.slug,
                        blog_entry_id=blog_entry_id,
                        blog_entry_slug=blog_entry.slug)

    user_permissions = UserPermissions(request.user, blog_entry.blog,
                                       blog_entry)
    if not user_permissions.can_show_blog_entry:
        raise Http404()

    if request.user != blog_entry.blog.bloger:
        blog_entry.visited += 1
        blog_entry.save()

    comment_entry_form = CommentForm(request.POST or None,
                                     blog_entry=blog_entry,
                                     user=request.user)
    if comment_entry_form.is_valid():
        comment_entry_form.save()

    comments = Comments.objects.filter(blog_entry_id=blog_entry_id)

    pictures = []
    for picture_object in blog_entry.pictures_json:
        url = picture_object['url']
        title = picture_object['title']
        pictures.append((url, title))

    related = BlogEntry.objects.only(
        'blog', 'slug', 'title', 'first_picture_url', 'summary',)\
        .filter(is_active=True, status=blog_entry_states.published,
                blog__status=moderation_states.accepted,
                blog__is_active=True).order_by('-visited').exclude(
        id=blog_entry.id)

    return {
        'blog': blog_entry.blog,
        'blog_entry': blog_entry,
        'blog_entry_states': blog_entry_states,
        'user_permissions': user_permissions,
        'comments': comments,
        'form': comment_entry_form,
        'moderation_states': moderation_states,
        'pictures': pictures,
        'related': related,
    }


@render_to('new_blog.html')
def add_blog(request):
    blog = Blog.objects.filter(bloger_id=request.user.id).first()

    if blog:
        if blog.status == moderation_states.accepted and blog.is_active:
            return redirect('blog', blog_slug=blog.slug)

        return {
            'can_add_blog': False,
            'blog': blog,
            'moderation_states': moderation_states,
        }

    add_blog_form = AddBlogForm(request.POST or None, request=request)

    if add_blog_form.is_valid():
        blog = add_blog_form.save()
        return redirect('configure_blog', blog_slug=blog.slug)

    return {
        'add_blog_form': add_blog_form,
        'can_add_blog': True,
    }


@login_required
@render_to('configure_blog.html')
def configure_blog(request, blog_slug, is_edited):
    blog = get_object_or_404(Blog, slug=blog_slug)
    user_permissions = UserPermissions(request.user, blog)
    if not user_permissions.can_configure_blog:
        raise Http404

    configure_blog_form = ConfigureBlogForm(request.POST or None, instance=blog)

    if configure_blog_form.is_valid():
        blog = configure_blog_form.save()
        return redirect('blog', blog_slug=blog.slug)

    return {
        'is_edited': is_edited,
        'blog': blog,
        'configure_blog_form': configure_blog_form,
    }


@login_required
@render_to('add_blog_entry.html')
def add_blog_entry(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug, bloger_id=request.user.id)
    user_permissions = UserPermissions(request.user, blog)
    if not user_permissions.can_add_entry:
        raise Http404

    add_entry_form = AddBlogEntryForm(request.POST or None, blog=blog)

    if add_entry_form.is_valid():
        blog_entry = add_entry_form.save()
        return redirect('blog_entry', blog_slug, blog_entry.id,
                        blog_entry.slug)

    last_blog_entry = BlogEntry.objects.only('id').last()

    return {
        'form': add_entry_form,
        'blog_entry_id': last_blog_entry.id + 1 if last_blog_entry else 1,
    }


@login_required
@render_to('add_blog_entry.html')
def edit_blog_entry(request, blog_slug, blog_entry_id, blog_entry_slug):
    blog_entry = get_object_or_404(BlogEntry, blog__bloger_id=request.user.id,
                                   blog__slug=blog_slug, id=blog_entry_id,
                                   is_active=True)

    user_permissions = UserPermissions(request.user, blog_entry.blog)
    if not user_permissions.can_add_entry and blog_entry.is_active:
        raise Http404

    edit_entry_form = EditBlogEntryForm(request.POST or None,
                                        instance=blog_entry)

    if edit_entry_form.is_valid():
        blog_entry = edit_entry_form.save()
        return redirect('blog_entry', blog_slug, blog_entry.id,
                        blog_entry.slug)

    return {
        'form': edit_entry_form,
        'is_edited': True,
        'first_picture_url': blog_entry.first_picture_url,
        'blog_entry_id': blog_entry.id
    }


@ajax_request
def load_photo(request):
    created_photo = None
    for photo in request.FILES.values():
        created_photo = Photo.objects.create(picture=photo)

    if created_photo:
        return {'info': 'sukces', 'name': created_photo.get_name()}
    else:
        return {'info': 'dupa'}


@ajax_request
def delete_entry(request, blog_entry_id):
    blog_entry = get_object_or_404(BlogEntry, blog__bloger_id=request.user.id,
                                   id=blog_entry_id,
                                   is_active=True)
    blog_entry.is_active=False
    blog_entry.save()


@ajax_request
def preview(request):
    markdown_text = request.POST.get('markdown_text', '')
    try:
        preview_body = markdown2.markdown(markdown_text)
        template_name = 'preview_template.html'
        context = {'preview_body': preview_body}
        rendered = render_to_string(template_name, context)
        return {
            'info': 'sukces',
            'preview_body': rendered,
        }
    except:
        return {
            'info': 'error',
        }


def get_paginated_page(qs, size, page_number):
    paginator = Paginator(qs, size)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page
