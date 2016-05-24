#!/usr/bin/env python
# encoding: utf-8

import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from enums import moderation_states, blog_entry_states
from models import Blog, BlogEntry


class RegistrationTestCase(TestCase):
    def setUp(self):
        super(RegistrationTestCase, self).setUp()

        self.registration_url = reverse('registration')

    def test_user_registration_not_matching_passwords(self):
        data_dict = {
            'username': 'abc',
            'password': 'a',
            'password_2': 'dupabiskiupa',
            'email': 'takisobie@wp.pl',
        }

        response = self.client.post(self.registration_url, data_dict)
        self.assertEquals(response.status_code, 302)

        self.assertEquals(
            User.objects.filter(username='Nowy użytkownik').exists(), False)

    def test_user_registration_without_require_parameter(self):
        data_dict = {
            'username': '',
            'password': 'a',
            'password_2': 'a',
            'email': 'takisobie@wp.pl',
        }

        response = self.client.post(self.registration_url, data_dict)
        self.assertEquals(response.status_code, 302)

        self.assertEquals(
            User.objects.filter(username='Nowy użytkownik').exists(), False)

    def test_user_registration(self):
        data_dict = {
            'username': 'abc',
            'password': 'a',
            'password_2': 'a',
            'email': 'takisobie@wp.pl',
        }

        response = self.client.post(self.registration_url, data_dict)
        self.assertEquals(response.status_code, 302)

        self.assertEquals(
            User.objects.filter(username=data_dict['username']).exists(), True)


class LoginTestCase(TestCase):
    def setUp(self):
        super(LoginTestCase, self).setUp()

        # create user
        self.user1 = User.objects.create_user(
            username='customer1', email='customer1@test.com', password='1234')

        self.url = '{0}?{1}'.format(
            reverse('login'), 'next=/admin/moje_strony/')

    def test_login(self):
        login_data_dict = {
            'username': 'customer1',
            'password': '1234',
        }

        response = self.client.post(self.url, login_data_dict)
        self.assertEquals(response.status_code, 302)
        self.assertEqual(
            response.url, 'http://testserver/admin/moje_strony/')

    def test_login_wrong_password(self):
        login_data_dict = {
            'username': 'customer1',
            'password': 'strzelam!!!',
        }

        response = self.client.post(self.url, login_data_dict)
        self.assertEquals(response.status_code, 200)


class AddBlogTestCase(TestCase):
    def setUp(self):
        super(AddBlogTestCase, self).setUp()

        # create users
        self.user1 = User.objects.create_user(
            username='customer1', email='customer1@test.com', password='1234')

        self.user2 = User.objects.create_user(
            username='customer2', email='customer2@test.com', password='1234')

        # create blog
        self.blog1 = Blog.objects.create(
            name=u'ogórki', slug='ogorki', bloger=self.user2,
            avatar_url='blabla.jpg', headline_picture_url='blabla.jpg'
        )

        self.add_blog_url = reverse('add_blog')

        self.client.login(username='customer1', password='1234')

    def test_add_blog(self):
        data_dict = {'name': 'szczurki'}
        response = self.client.post(self.add_blog_url, data_dict)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Blog.objects.filter(name=data_dict['name']).exists(), True)

        resp_url = reverse(
            'configure_blog', kwargs={'blog_slug': data_dict['name']})
        self.assertTrue(response.url.endswith(resp_url))

    def test_add_blog_if_user_got_a_blog(self):
        self.client.login(username='customer2', password='1234')

        data_dict = {'name': 'dziurki'}
        response = self.client.post(self.add_blog_url, data_dict)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Blog.objects.filter(name=data_dict['name']).count(), 0)

        msg = u'Twój blog nie został jeszcze aktywowany.'
        self.assertTrue(msg in response.content.decode('utf8'))


class ConfigureBlogTestCase(TestCase):
    def setUp(self):
        super(ConfigureBlogTestCase, self).setUp()

        # create users
        self.user1 = User.objects.create_user(
            username='customer1', email='customer1@test.com', password='1234')

        self.user2 = User.objects.create_user(
            username='customer2', email='customer2@test.com', password='1234')

        # create blog
        self.blog1 = Blog.objects.create(
            name='szczurki', slug='ogorki', bloger=self.user1,
            avatar_url='blabla1.jpg', headline_picture_url='blabla2.jpg'
        )

        self.configure_blog_url = reverse(
            'configure_blog', kwargs={'blog_slug': self.blog1.slug})

        self.client.login(username='customer1', password='1234')

    def test_change_blog_configuration(self):
        data_dict = {
            'name': 'otworki',
            'description': ' ',
            'avatar_url': 'blabla1.jpg',
            'headline_picture_url': 'blabla2.jpg',
        }

        response = self.client.post(self.configure_blog_url, data_dict)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Blog.objects.filter(name=data_dict['name']).exists(), True)

    def test_change_not_allowed_field(self):
        data_dict = {
            'name': 'otworki',
            'description': 'taki tam blog',
            'avatar_url': 'blabla1.jpg',
            'headline_picture_url': 'blabla2.jpg',
            'slug': 'dupabiskupa',
        }
        self.client.post(self.configure_blog_url, data_dict)

        self.assertEqual(
            Blog.objects.filter(slug=data_dict['slug']).exists(), False)

    def test_change_not_user_blog(self):
        data_dict = {
            'name': 'otworki',
            'description': ' ',
            'avatar_url': 'blabla1.jpg',
            'headline_picture_url': 'blabla2.jpg',
        }

        self.client.login(username='customer2', password='1234')
        response = self.client.post(self.configure_blog_url, data_dict)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Blog.objects.filter(name=data_dict['name']).exists(), False)


class AddBlogEntryTestCase(TestCase):
    def setUp(self):
        super(AddBlogEntryTestCase, self).setUp()

        # create users
        self.user1 = User.objects.create_user(
            username='customer1', email='customer1@test.com', password='1234')

        self.user2 = User.objects.create_user(
            username='customer2', email='customer2@test.com', password='1234')

        # create blog
        self.blog1 = Blog.objects.create(
            name='szczurki', slug='ogorki', bloger=self.user1,
            avatar_url='blabla1.jpg', headline_picture_url='blabla2.jpg'
        )

        self.add_blog_entry_url = reverse(
            'add_blog_entry', kwargs={'blog_slug': self.blog1.slug})

        self.client.login(username='customer1', password='1234')

    def test_add_blog_entry(self):
        post_dict = {
            'title': u'Szczurki lubią ser',
            'summary': u'Szczurki lubią ser i mieszkają w kanałach.',
            'first_picture_url': '',
            'pictures_json': '',
            'markdown_body': 'abcd',
            'comments_allowed': False,
        }
        response = self.client.post(self.add_blog_entry_url, post_dict)
        self.assertEqual(response.status_code, 302)

    def test_add_blog_entry_invalid_form(self):
        post_dict = {
            'title': u'Szczurki lubią ser',
            'summary': '',
            'first_picture_url': '',
            'pictures_json': '',
            'markdown_body': 'abcd',
            'comments_allowed': False,
        }
        response = self.client.post(self.add_blog_entry_url, post_dict)
        self.assertEqual(response.status_code, 200)

    def test_add_blog_entry_if_user_is_not_blog_owner(self):
        self.client.login(username='customer2', password='1234')

        response = self.client.post(self.add_blog_entry_url, {})
        self.assertEqual(response.status_code, 404)

    def test_add_blog_entry_if_blog_is_rejected(self):
        self.blog1.status = moderation_states.rejected
        self.blog1.save()

        response = self.client.post(self.add_blog_entry_url, {})
        self.assertEqual(response.status_code, 404)


class EditBlogEntryTestCase(TestCase):
    def setUp(self):
        super(EditBlogEntryTestCase, self).setUp()

        # create users
        self.user1 = User.objects.create_user(
            username='customer1', email='customer1@test.com', password='1234')

        self.user2 = User.objects.create_user(
            username='customer2', email='customer2@test.com', password='1234')

        # create blog
        self.blog1 = Blog.objects.create(
            name='szczurki', slug='ogorki', bloger=self.user1,
            avatar_url='blabla1.jpg', headline_picture_url='blabla2.jpg'
        )

        # create blog entry
        self.blog_entry_1 = BlogEntry.objects.create(
            title=u'Szczurki lubią ser', summary='Bo juz takie som',
            first_picture_url='', pictures_json='', markdown_body='abcd',
            comments_allowed=False, blog=self.blog1, slug='a_jak_nie_jak_tak'
        )

        url_kwargs = {
            'blog_slug': self.blog1.slug,
            'blog_entry_id': self.blog_entry_1.id,
            'blog_entry_slug': self.blog_entry_1.slug,
        }

        self.edit_blog_entry_url = reverse('edit_blog_entry', kwargs=url_kwargs)

        self.client.login(username='customer1', password='1234')

    def test_edit_blog_entry(self):
        post_dict = {
            'title': u'Szczurki są obrzydliwe.',
            'summary': u'Kto by chciał pogłaskać szczurka...',
            'first_picture_url': '',
            'pictures_json': '',
            'markdown_body': 'abcd',
            'comments_allowed': True,
        }
        response = self.client.post(self.edit_blog_entry_url, post_dict)
        self.assertEqual(response.status_code, 302)

    def test_edit_blog_entry_invalid_form(self):
        post_dict = {
            'title': '',
            'summary': u'Kto by chciał pogłaskać szczurka...',
            'first_picture_url': '',
            'pictures_json': '',
            'markdown_body': 'abcd',
            'comments_allowed': True,
        }
        response = self.client.post(self.edit_blog_entry_url, post_dict)
        self.assertEqual(response.status_code, 200)

    def test_edit_blog_entry_bloger_whose_blog_is_rejected(self):
        self.blog1.status = moderation_states.rejected
        self.blog1.save()

        response = self.client.post(self.edit_blog_entry_url, {})
        self.assertEqual(response.status_code, 404)

    def test_edit_archival_blog_entry(self):
        self.blog_entry_1.is_active = False
        self.blog_entry_1.save()

        response = self.client.post(self.edit_blog_entry_url, {})
        self.assertEqual(response.status_code, 404)


class ArchiveBlogEntryTestCase(TestCase):
    def setUp(self):
        super(ArchiveBlogEntryTestCase, self).setUp()

        # create users
        self.user1 = User.objects.create_user(
            username='customer1', email='customer1@test.com', password='1234')

        self.user2 = User.objects.create_user(
            username='customer2', email='customer2@test.com', password='1234')

        # create blog
        self.blog1 = Blog.objects.create(
            name='szczurki', slug='ogorki', bloger=self.user1,
            avatar_url='blabla1.jpg', headline_picture_url='blabla2.jpg'
        )

        # create blog entry
        self.blog_entry_1 = BlogEntry.objects.create(
            title=u'Szczurki lubią ser', summary='Bo juz takie som',
            first_picture_url='', pictures_json='', markdown_body='abcd',
            comments_allowed=False, blog=self.blog1, slug='a_jak_nie_jak_tak'
        )

        url_kwargs = {
            'blog_entry_id': self.blog_entry_1.id,
        }

        self.archive_blog_entry_url = reverse('delete_entry', kwargs=url_kwargs)

        self.client.login(username='customer1', password='1234')

    def test_archive_blog_entry(self):
        response = self.client.post(self.archive_blog_entry_url, {})
        self.assertEqual(response.status_code, 200)
        archival_blog_entry = BlogEntry.objects.get(id=1)
        self.assertFalse(archival_blog_entry.is_active)

    def test_archive_archival_entry(self):
        self.blog_entry_1.is_active = False
        self.blog_entry_1.save()

        response = self.client.post(self.archive_blog_entry_url, {})
        self.assertEqual(response.status_code, 404)

    def test_archive_not_own_entry(self):
        self.client.login(username='customer2', password='1234')

        response = self.client.post(self.archive_blog_entry_url, {})
        self.assertEqual(response.status_code, 404)
