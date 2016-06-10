# -*- coding: utf-8 -*-

from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin

#from admintrans.admin import *

from project.models import Country, Region, Town, Brand, Dealer, DealerSeance, DealerPay, DealerBanner, DealerBlog, DealerComment, DealerMessage, Category, CategoryItem, Bookmark, Partner

#######################################################################################################################
#######################################################################################################################

#Страна
class CountryAdmin(AdminImageMixin, admin.ModelAdmin):
	list_display = ('title', 'slug', 'cod', 'small_image', 'is_active', 'sort')
	search_fields = ('title', 'slug')
	list_filter = ('is_active',)
	list_editable = ('is_active', 'sort')

admin.site.register(Country, CountryAdmin)

#Область
class RegionAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'country', 'is_active', 'sort')
	search_fields = ('title', 'slug')
	list_filter = ('country', 'is_active')
	list_editable = ('is_active', 'sort')

admin.site.register(Region, RegionAdmin)

#Город
class TownAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'region', 'country', 'is_main', 'is_capital', 'is_default', 'is_active', 'sort')
	search_fields = ('title', 'slug')
	list_filter = ('is_main', 'region__country', 'region', 'is_active')
	list_editable = ('is_main', 'is_active', 'sort')

admin.site.register(Town, TownAdmin)

#######################################################################################################################
#######################################################################################################################

#Марка автомобиля
class BrandAdmin(AdminImageMixin, admin.ModelAdmin):
	list_display = ('title', 'slug', 'small_image', 'is_popular', 'is_active', 'sort')
	search_fields = ('title', 'slug')
	list_filter = ('is_active',)
	list_editable = ('is_popular', 'is_active', 'sort')

admin.site.register(Brand, BrandAdmin)

#######################################################################################################################
#######################################################################################################################

#Сеансы
class DealerSeanceInline(admin.TabularInline):
	model = DealerSeance
	extra = 0
	
#Платежи дилера
class DealerPayInline(admin.TabularInline):
	model = DealerPay
	extra = 0
	
#Баннеры дилера
class DealerBannerInline(admin.TabularInline):
	model = DealerBanner
	extra = 0
	
#Закладки дилера
class BookmarkInline(admin.TabularInline):
	model = Bookmark
	extra = 0
	
#Партнеры
class PartnerInline(admin.TabularInline):
	model = Partner
	fk_name = 'dealer'
	extra = 0
	
#Дилер
class DealerAdmin(AdminImageMixin, admin.ModelAdmin):
	inlines = [DealerSeanceInline, DealerPayInline, DealerBannerInline, BookmarkInline, PartnerInline]
	list_display = ('title', 'name', 'user', 'small_image', 'is_license', 'is_banned', 'banned_to', 'active_to', 'is_active', 'sort')
	search_fields = ('title', 'name')
	list_filter = ('is_license', 'is_banned', 'banned_to', 'active_to', 'is_active',)
	list_editable = ('is_banned', 'is_active', 'sort')
	filter_horizontal = ('town', 'brand')

admin.site.register(Dealer, DealerAdmin)

#######################################################################################################################
#######################################################################################################################

class DealerCommentInline(admin.StackedInline):
	model = DealerComment
	extra = 0
	
#Блог дилера
class DealerBlogAdmin(admin.ModelAdmin):
	inlines = [DealerCommentInline]
	list_display = ('title', 'slug', 'dealer', 'date', 'is_active', 'sort')
	search_fields = ('title', 'slug')
	list_filter = ('date', 'is_active', 'dealer')
	list_editable = ('is_active', 'sort')

admin.site.register(DealerBlog, DealerBlogAdmin)

#######################################################################################################################
#######################################################################################################################

#Сообщения дилера
class DealerMessageAdmin(admin.ModelAdmin):
	list_display = ('dealer', 'fdealer', 'date', 'is_read')
	list_filter = ('date', 'dealer', 'fdealer')

admin.site.register(DealerMessage, DealerMessageAdmin)

#######################################################################################################################
#######################################################################################################################

class CategoryItemInline(admin.TabularInline):
	model = CategoryItem
	extra = 0
	
class CategoryAdmin(admin.ModelAdmin):
	inlines = [CategoryItemInline]
	list_display = ('title', 'slug', 'dealer', 'date', 'is_main', 'is_active', 'sort')
	search_fields = ('title', 'slug')
	list_filter = ('date', 'is_main', 'is_active', 'dealer')
	list_editable = ('is_main', 'is_active', 'sort')

admin.site.register(Category, CategoryAdmin)

#######################################################################################################################
#######################################################################################################################