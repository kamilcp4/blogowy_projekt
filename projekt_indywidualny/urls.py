from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login

from blog import urls as blog_urls
from . import settings

urlpatterns = [
    url(r'^accounts/login/$', login, name='login'),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(blog_urls)),

]
