# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce import models as TinymceField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from pytils.translit import slugify
import datetime
import re
import os

from sorl.thumbnail import ImageField as SorlImageField
from sorl.thumbnail.shortcuts import get_thumbnail, delete

try:
	import Image
except ImportError:
	try:
		from PIL import Image
	except ImportError:
		raise ImportError("The Python Imaging Library was not found.")

#######################################################################################################################
#######################################################################################################################

#Страна
class Country(models.Model):
	title = models.CharField(max_length=500, verbose_name=_("title"))
	slug = models.SlugField(unique=True, max_length=500, verbose_name=_("slug"), blank=True)
	cod = models.CharField(max_length=50, verbose_name=_("cod"))
	image = SorlImageField(upload_to=u'upload/country/', verbose_name=_("image"))
	is_active = models.BooleanField(verbose_name=_("is active"), default=True)
	sort = models.IntegerField(verbose_name=_("sort"), default=0)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	def clean(self):
		r = re.compile('^([a-zA-Z0-9_-]+)\.(jpg|png|bmp|gif)$')
		if self.image:
			if not r.findall(os.path.split(self.image.url)[1]):
				raise ValidationError(_("File name validation error."))
				
	def small_image(self):
		if self.image:
			f = get_thumbnail(self.image, '30x20', crop='center', quality=99)
			html = '<a href="%s"><img src="%s" title="%s" /></a>'
			return html % (self.image.url, f.url, self.title)
		else: return _("No image")

	small_image.short_description = _("Image")
	small_image.allow_tags = True
	
	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Country, self).save(*args, **kwargs)
	
	class Meta: 
		verbose_name = _("country")
		verbose_name_plural = _("countrys")
		ordering = ['sort', 'title']
		
#Область
class Region(models.Model):
	country = models.ForeignKey(Country, verbose_name=_("country"))
	title = models.CharField(max_length=500, verbose_name=_("title"))
	slug = models.SlugField(unique=True, max_length=500, verbose_name=_("slug"), blank=True)
	is_active = models.BooleanField(verbose_name=_("is active"), default=True)
	sort = models.IntegerField(verbose_name=_("sort"), default=0)
	
	def __unicode__(self):
		return u'%s' % self.title
	
	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Region, self).save(*args, **kwargs)
	
	class Meta: 
		verbose_name = _("region")
		verbose_name_plural = _("regions")
		ordering = ['sort', 'title']
		
#Город
class Town(models.Model):
	region = models.ForeignKey(Region, verbose_name=_("region"))
	title = models.CharField(max_length=500, verbose_name=_("title"))
	slug = models.SlugField(max_length=500, verbose_name=_("slug"), blank=True)
	is_main = models.BooleanField(verbose_name=_("is main"), default=True) #отображать на главной странице
	is_capital = models.BooleanField(verbose_name=_("is capital"), default=False) #Столица/областной центр
	is_default = models.BooleanField(verbose_name=_("is default"), default=False) #Город по умолчанию, если не определили
	is_active = models.BooleanField(verbose_name=_("is active"), default=True)
	sort = models.IntegerField(verbose_name=_("sort"), default=0)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	def country(self):
		return self.region.country
	country.short_description = _("Country")
	
	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		if self.is_default:
			Town.objects.filter(is_default=True).update(is_default=False)
		super(Town, self).save(*args, **kwargs)
	
	class Meta: 
		verbose_name = _("town")
		verbose_name_plural = _("towns")
		ordering = ['sort', 'title']
		
#######################################################################################################################
#######################################################################################################################

#Марка автомобиля
class Brand(models.Model):
	title = models.CharField(max_length=500, verbose_name=_("title"))
	slug = models.SlugField(unique=True, max_length=500, verbose_name=_("slug"), blank=True)
	image = SorlImageField(upload_to=u'upload/brand/', verbose_name=_("image"), blank=True, null=True)
	is_popular = models.BooleanField(verbose_name=_("is popular"), default=False)
	is_active = models.BooleanField(verbose_name=_("is active"), default=True)
	sort = models.IntegerField(verbose_name=_("sort"), default=0)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	def clean(self):
		r = re.compile('^([a-zA-Z0-9_-]+)\.(jpg|png|bmp|gif)$')
		if self.image:
			if not r.findall(os.path.split(self.image.url)[1]):
				raise ValidationError(_("File name validation error."))
				
	def small_image(self):
		if self.image:
			f = get_thumbnail(self.image, '80x80', crop='center', quality=99)
			html = '<a href="%s"><img src="%s" title="%s" /></a>'
			return html % (self.image.url, f.url, self.title)
		else: return _("No image")

	small_image.short_description = _("Image")
	small_image.allow_tags = True
	
	def get_dealers(self):
		return self.dealers.filter(is_banned=False, is_active=True)
	
	def get_count_dealers(self):
		return self.get_dealers().count()
	
	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Brand, self).save(*args, **kwargs)
	
	class Meta: 
		verbose_name = _("brand")
		verbose_name_plural = _("brands")
		ordering = ['sort', 'title']
		
#######################################################################################################################
#######################################################################################################################

#Дилер
class Dealer(models.Model):
	user = models.OneToOneField(User, verbose_name=_("user"))
	town = models.ManyToManyField(Town, verbose_name=_("town"))
	brand = models.ManyToManyField(Brand, verbose_name=_("brand"), related_name='dealers')
	
	title = models.CharField(max_length=500, verbose_name=_("title"))
	slug = models.SlugField(max_length=500, verbose_name=_("slug"), blank=True)
	image = SorlImageField(upload_to=u'upload/dealer/', verbose_name=_("image"), blank=True, null=True, help_text=_('Help text image 250x'))
	text = models.TextField(max_length=100000, verbose_name=_("text"), blank=True)
	
	name = models.CharField(max_length=500, verbose_name=_("org. name")) #название организации
	kpp = models.CharField(verbose_name=_("org. KPP"), max_length=9, blank=True) #КПП
	ogrn = models.CharField(verbose_name=_("org. OGRN"), max_length=15, blank=True) #ОГРН
	adr_reg = models.CharField(verbose_name=_("org. address reg."), max_length=500, blank=True) #адрес по месту регистрации организации
	adr = models.CharField(verbose_name=_("org. address"), max_length=500, blank=True) #адрес местонахождения организации
	head = models.CharField(verbose_name=_("org. head"), max_length=500, blank=True) #должность руководителя организации
	base = models.CharField(verbose_name=_("org. base"), max_length=500, blank=True) #действующего на основании
	fio_head = models.CharField(verbose_name=_("org. fio head"), max_length=500, blank=True) #ФИО руководителя организации
	inn = models.CharField(verbose_name=_("org. inn"), max_length=12, blank=True) #ИНН
	rs = models.CharField(verbose_name=_("org. rs"), max_length=20, blank=True) #Р/С
	bank = models.CharField(verbose_name=_("org. bank's name"), max_length=500, blank=True) #наименование банка
	kors = models.CharField(verbose_name=_("org. kors"), max_length=500, blank=True) #кор/сч
	bik = models.CharField(verbose_name=_("org. bik"), max_length=9, blank=True) #БИК
	fio_contact = models.CharField(verbose_name=_("org. fio contact"), max_length=500, blank=True) #ФИО контактного лица
	email = models.CharField(verbose_name=_("org. e-mail"), max_length=100, blank=True)
	phone = models.CharField(verbose_name=_("org. phone"), max_length=100, blank=True)
	
	is_license = models.BooleanField(verbose_name=_("is license"), default=False) #Согласен ли с правилами
	
	is_banned = models.BooleanField(verbose_name=_("is banned"), default=False) #Забанен ли дилер
	banned_to = models.DateTimeField(verbose_name=_("banned to"), blank=True, null=True) #До какого времени забанен
	
	active_to = models.DateTimeField(verbose_name=_("active to"), blank=True, null=True) #До какого времени активен
	
	is_active = models.BooleanField(verbose_name=_("is active"), default=True)
	sort = models.IntegerField(verbose_name=_("sort"), default=0)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	def clean(self):
		r = re.compile('^([a-zA-Z0-9_-]+)\.(jpg|png|bmp|gif)$')
		if self.image:
			if not r.findall(os.path.split(self.image.url)[1]):
				raise ValidationError(_("File name validation error."))
				
	def small_image(self):
		if self.image:
			f = get_thumbnail(self.image, '80x80', crop='center', quality=99)
			html = '<a href="%s"><img src="%s" title="%s" /></a>'
			return html % (self.image.url, f.url, self.title)
		else: return _("No image")

	small_image.short_description = _("Image")
	small_image.allow_tags = True
	
	def new_messages(self, ds):
		return self.from_dealers.filter(fdealer=ds, is_read=False)
	
	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Dealer, self).save(*args, **kwargs)
	
	class Meta: 
		verbose_name = _("dealer")
		verbose_name_plural = _("dealers")
		ordering = ['sort',]
		
#######################################################################################################################
#######################################################################################################################

#Сеансы
class DealerSeance(models.Model):
	dealer = models.ForeignKey(Dealer, verbose_name=_("dealer"))
	ip = models.CharField(max_length=500, verbose_name=_("ip"))
	date = models.DateTimeField(verbose_name=_("date"), default=datetime.datetime.now())
	
	def __unicode__(self):
		return u'%s / %s (%s)' % (self.dealer, self.ip, self.date.strftime("%d.%m.%Y %H:%M"))
		
	def save(self, *args, **kwargs):
		dss = DealerSeance.objects.filter(dealer=self.dealer).order_by('id')
		if dss.count() > 30:
			dss[0].delete()
		super(DealerSeance, self).save(*args, **kwargs)
		
	class Meta: 
		verbose_name = _("seance") 
		verbose_name_plural = _("seances")
		ordering = ['-id']

#######################################################################################################################
#######################################################################################################################

#Платежи дилера
class DealerPay(models.Model):
	dealer = models.ForeignKey(Dealer, verbose_name=_("dealer"))
	title = models.TextField(max_length=1000, verbose_name=_("title"))
	date = models.DateTimeField(verbose_name=_("date"), default=datetime.datetime.now())
	sum = models.IntegerField(verbose_name=_("sum"), default=0)
	
	def __unicode__(self):
		return u'%s (%s) / %s / %d' % (self.dealer, self.date.strftime("%d.%m.%Y %H:%M"), self.title, self.sum)
	
	class Meta: 
		verbose_name = _("pay")
		verbose_name_plural = _("pays")
		ordering = ['-date']
		
#######################################################################################################################
#######################################################################################################################

#Баннеры дилера
class DealerBanner(models.Model):
	dealer = models.ForeignKey(Dealer, verbose_name=_("dealer"))
	title = models.CharField(max_length=500, verbose_name=_("title"))
	image = SorlImageField(upload_to=u'upload/banner/image/', verbose_name=_("image"), blank=True, null=True, help_text=_("Help text image or flash banner 250x100 px"))
	flash = models.FileField(upload_to=u'upload/banner/flash/', verbose_name=_("flash"), blank=True, null=True)
	width = models.IntegerField(verbose_name=_("width"), default=250, help_text=_("0<width<250"))
	height = models.IntegerField(verbose_name=_("height"), default=200)
	site = models.URLField(verbose_name=_("site"), help_text=_("Example: http://web-aspect.ru"), blank=True)
	is_active = models.BooleanField(verbose_name=_("is active"), default=True)
	sort = models.IntegerField(verbose_name=_("order"), default=0)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	@models.permalink
	def get_admin_url(self):
		return ('banner_admin_url', (), {'id':self.id})
		
	def clean(self):
		r = re.compile('^([a-zA-Z0-9_-]+)\.([a-zA-Z0-9_-]+)$')
		if self.image:
			if not r.findall(os.path.split(self.image.url)[1]):
				raise ValidationError(_("File name validation error"))
		if self.flash:
			if not r.findall(os.path.split(self.flash.url)[1]):
				raise ValidationError(_("File name validation error"))
				
		if self.width > 250:
			raise ValidationError(_("Error width banner."))
	
	class Meta: 
		verbose_name = _("banner")
		verbose_name_plural = _("banners")
		ordering = ['sort', '-id']
		
#######################################################################################################################
#######################################################################################################################

#Блог дилера
class DealerBlog(models.Model):
	dealer = models.ForeignKey(Dealer, verbose_name=_("dealer"))
	date = models.DateTimeField(verbose_name=_("date"), default=datetime.datetime.now())
	title = models.CharField(max_length=500, verbose_name=_("title"))
	slug = models.SlugField(max_length=500, verbose_name=_("slug"), blank=True)
	text = models.TextField(max_length=100000, verbose_name=_("text"), blank=True)
	is_active = models.BooleanField(verbose_name=_("is active"), default=True)
	sort = models.IntegerField(verbose_name=_("order"), default=0)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	@models.permalink
	def get_item_url(self):
		return ('blog_item_url', (), {'id':self.id, 'slug': self.slug})
		
	@models.permalink
	def get_admin_url(self):
		return ('blog_admin_url', (), {'id':self.id})
		
	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(DealerBlog, self).save(*args, **kwargs)
		
	def get_comments(self):
		return self.blogcomments.filter(is_active=True)
		
	def get_no_active_comments(self):
		return self.blogcomments.filter(is_active=False).count()
		
	class Meta: 
		verbose_name = _("blog's item") 
		verbose_name_plural = _("blog")
		ordering = ['sort', 'id']
		
#######################################################################################################################
#######################################################################################################################

class DealerComment(models.Model):
	item = models.ForeignKey(DealerBlog, verbose_name=_("item"), related_name="blogcomments")
	date = models.DateTimeField(verbose_name=_("date"))
	name = models.CharField(max_length=500, verbose_name=_("name"))
	phone = models.CharField(max_length=50, verbose_name=_("phone"), blank=True)
	org = models.CharField(max_length=500, verbose_name=_("org"), blank=True)
	post = models.CharField(max_length=500, verbose_name=_("post"), blank=True)
	email = models.CharField(max_length=500, verbose_name=_("email"))
	text = models.TextField(max_length=10000, verbose_name=_("text"))
	is_active = models.BooleanField(verbose_name=_("is active"), default=False)
	sort = models.IntegerField(verbose_name=_("order"), default=0)
	
	def __unicode__(self):
		return u'%s - %s (%s)' % (self.item, self.name, self.date.strftime("%d.%m.%Y %H:%M"))
		
	class Meta: 
		verbose_name = _("blog's item's comment") 
		verbose_name_plural = _("comments")
		ordering = ['sort', '-id']

#######################################################################################################################
#######################################################################################################################

class DealerMessage(models.Model):
	dealer = models.ForeignKey(Dealer, verbose_name=_("dealer"), related_name="from_dealers")
	fdealer = models.ForeignKey(Dealer, verbose_name=_("for dealer"), related_name="for_dealers")
	date = models.DateTimeField(verbose_name=_("date"), default=datetime.datetime.now())
	text = models.TextField(max_length=10000, verbose_name=_("text"))
	is_read = models.BooleanField(verbose_name=_("is read"), default=False)
	
	def __unicode__(self):
		return u'%s - %s (%s)' % (self.dealer.title, self.fdealer.title, self.date.strftime("%d.%m.%Y %H:%M"))
		
	class Meta: 
		verbose_name = _("message") 
		verbose_name_plural = _("messages")
		ordering = ['-id']

#######################################################################################################################
#######################################################################################################################

class Category(models.Model):
	dealer = models.ForeignKey(Dealer, verbose_name=_("dealer"), blank=True, null=True)
	date = models.DateTimeField(verbose_name=_("date"), default=datetime.datetime.now())
	title = models.CharField(max_length=500, verbose_name=_("title"))
	slug = models.SlugField(max_length=500, verbose_name=_("slug"), blank=True)
	is_main = models.BooleanField(verbose_name=_("is main"), default=False)
	is_active = models.BooleanField(verbose_name=_("is active"), default=True)
	sort = models.IntegerField(verbose_name=_("order"), default=0)
	
	def __unicode__(self):
		return u'%s' % self.title
		
	def get_items(self):
		return self.items.all()
		
	def get_active_items(self):
		return self.items.filter(is_active=True)
		
	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Category, self).save(*args, **kwargs)
		
	class Meta: 
		verbose_name = _("category") 
		verbose_name_plural = _("categoryes")
		ordering = ['is_main', 'sort', '-id']

#######################################################################################################################
#######################################################################################################################

class CategoryItem(models.Model):
	category = models.ForeignKey(Category, verbose_name=_("category"), related_name='items')
	dealer = models.ForeignKey(Dealer, verbose_name=_("dealer"))
	date = models.DateTimeField(verbose_name=_("date"), default=datetime.datetime.now())
	text = models.TextField(max_length=1000, verbose_name=_("text"))
	
	f = models.CharField(max_length=100, verbose_name=_("f"), blank=True) #фамилия
	i = models.CharField(max_length=100, verbose_name=_("i"), blank=True) #имя
	o = models.CharField(max_length=100, verbose_name=_("o"), blank=True) #отчество
	npas = models.CharField(max_length=10, verbose_name=_("npas"), blank=True) #номер паспорта
	spas = models.CharField(max_length=10, verbose_name=_("spas"), blank=True) #серия паспорта
	rdate = models.DateField(verbose_name=_("date r."), blank=True, null=True, help_text=_("Help text rdate xx.xx.xxxx")) #дата рождения
	
	is_only_town = models.BooleanField(verbose_name=_("is only my town's dealers"), default=False)
	is_only_brand = models.BooleanField(verbose_name=_("is only my brands' dealers"), default=False)
	
	is_active = models.BooleanField(verbose_name=_("is active"), default=True)
	sort = models.IntegerField(verbose_name=_("order"), default=0)
	
	def __unicode__(self):
		return u'%s / %s - %s (%s)' % (self.category, self.dealer, self.text, self.date.strftime("%d.%m.%Y %H:%M"))
		
	class Meta: 
		verbose_name = _("item") 
		verbose_name_plural = _("items")
		ordering = ['sort', '-id']

#######################################################################################################################
#######################################################################################################################

#Закладки
class Bookmark(models.Model):
	dealer = models.ForeignKey(Dealer, verbose_name=_("dealer"))
	category = models.ForeignKey(Category, verbose_name=_("category"))
	date = models.DateTimeField(verbose_name=_("date"), default=datetime.datetime.now())
	
	def __unicode__(self):
		return u'%s / %s (%s)' % (self.dealer, self.category, self.date.strftime("%d.%m.%Y %H:%M"))
		
	class Meta: 
		verbose_name = _("bookmark") 
		verbose_name_plural = _("bookmarks")
		ordering = ['-id']

#######################################################################################################################
#######################################################################################################################

#Партнеры
class Partner(models.Model):
	dealer = models.ForeignKey(Dealer, verbose_name=_("dealer"), related_name='dealers')
	pdealer = models.ForeignKey(Dealer, verbose_name=_("partner"), related_name='partners')
	date = models.DateTimeField(verbose_name=_("date"), default=datetime.datetime.now())
	
	def __unicode__(self):
		return u'%s / %s (%s)' % (self.dealer, self.pdealer, self.date.strftime("%d.%m.%Y %H:%M"))
		
	class Meta: 
		verbose_name = _("partner") 
		verbose_name_plural = _("partners")
		ordering = ['-id']

#######################################################################################################################
#######################################################################################################################