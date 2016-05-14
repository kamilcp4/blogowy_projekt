from django.contrib import admin

from .models import Blog, BlogEntry, Photo, Comments

admin.site.register(Blog)
admin.site.register(BlogEntry)
admin.site.register(Photo)
admin.site.register(Comments)
