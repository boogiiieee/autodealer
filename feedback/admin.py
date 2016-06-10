# -*- coding: utf-8 -*-

from django.contrib import admin
from feedback.models import Item as Items

class ItemsAdmin(admin.ModelAdmin):
	list_display = ('id', 'dealer', 'name', 'email', 'phone', 'date')
	list_filter = ('date',)
	
admin.site.register(Items, ItemsAdmin)
