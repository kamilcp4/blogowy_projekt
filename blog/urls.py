from django.conf.urls import url, patterns

urlpatterns = patterns('blog.views',
    url(r'^preview$', 'preview'),
    url(r'^regulamin/$', 'statute', name='statute'),
    url(r'^rejestracja/$', 'registration', name='registration'),
    url(r'^logout/$', 'logout_page'),
    url(r'^send_photo$', 'load_photo'),
    url(r'^delete_entry/(?P<blog_entry_id>[\d]+)$', 'delete_entry', name='delete_entry'),
    url(r'^$', 'blogs', name='blogs'),
    url(r'^dodaj_blog$', 'add_blog', name='add_blog'),
    url(r'^(?P<blog_slug>[\w-]+)/konfiguracja_bloga$', 'configure_blog',
        {'is_edited': False}, name='configure_blog'),
    url(r'^(?P<blog_slug>[\w-]+)/edycja_bloga$', 'configure_blog',
        {'is_edited': True}, name='edit_blog'),
    url(r'^(?P<blog_slug>[\w-]+)/dodaj_wpis$', 'add_blog_entry',
        name='add_blog_entry'),
    url(r'^(?P<blog_slug>[\w-]+)/(?P<blog_entry_id>[\d]+)-'
        r'(?P<blog_entry_slug>[\w-]+)/edytuj_wpis$',
        'edit_blog_entry', name='edit_blog_entry'),
    url(r'^(?P<blog_slug>[\w-]+)$', 'main_blog_page', name='blog'),
    url(r'^(?P<blog_slug>[\w-]+)/(?P<blog_entry_id>[\d]+)-'
        r'(?P<blog_entry_slug>[\w-]+)$', 'blog_entry', name='blog_entry'),
)
