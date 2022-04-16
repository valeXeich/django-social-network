from django.contrib import admin

from .models import Group, GroupBan

admin.site.register(Group)
admin.site.register(GroupBan)
