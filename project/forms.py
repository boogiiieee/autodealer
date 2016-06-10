# -*- coding: utf-8 -*-

from django import forms
from captcha.fields import CaptchaField
from django.utils.translation import ugettext_lazy as _
from django.forms.models import inlineformset_factory
import re

from project.models import Town, Brand, Dealer, DealerBanner, DealerBlog, DealerComment, DealerMessage, Category, CategoryItem

#Поиск дилера
class DealerSearchForm(forms.Form):
	title = forms.CharField(max_length=500, label=_("Title org."), required=False)
	town = forms.ModelChoiceField(queryset = Town.objects.filter(is_active=True), label=_("Town org."), required=False)
	brand = forms.ModelChoiceField(queryset = Brand.objects.filter(is_active=True), label=_("Brand org."), required=False)

#Добавить комментарий	
class DealerCommentForm(forms.ModelForm):
	captcha = CaptchaField()
	
	class Meta:
		model = DealerComment
		fields = ('name', 'phone', 'org', 'post', 'email', 'text')
		
	def clean_name(self): 
		name = self.cleaned_data['name']
		if len(name) < 3:
			raise forms.ValidationError(_("Invalid name field"))
		return name
		
	def clean_email(self): 
		email = self.cleaned_data['email']
		r = re.compile('^[0-9a-zA-Z]+[-\._0-9a-zA-Z]*@[0-9a-zA-Z]+[-\._^0-9a-zA-Z]*[0-9a-zA-Z]+[\.]{1}[a-zA-Z]{2,6}$')
		if not r.findall(email):
			raise forms.ValidationError(_("Invalid email field"))
		return email
		
	def clean_text(self): 
		text = self.cleaned_data['text']
		if len(text) < 10:
			raise forms.ValidationError(_("Invalid text field"))
		return text

#Лицензионное соглашение	
class DealerAccountLicenseForm(forms.ModelForm):
	class Meta:
		model = Dealer
		fields = ('is_license',)
				
#Анкета дилера	
class DealerAccountForm(forms.ModelForm):
	class Meta:
		model = Dealer
		fields = ('title', 'image', 'text', 'name', 'kpp', 'ogrn', 'adr_reg', 'adr', 'head', 'base', 'fio_head', 'inn', 'rs', 'bank', 'kors', 'bik', 'fio_contact', 'email', 'phone', 'town', 'brand')
		
#Блог дилера
class DealerAccountBlogAddFormset(inlineformset_factory(DealerBlog, DealerComment, can_delete=True)):
    pass
	
class DealerAccountBlogAddForm(forms.ModelForm):
	class Meta:
		model = DealerBlog
		fields = ('title', 'text', 'is_active', 'sort')
		
#Баннер дилера	
class DealerAccountBannerAddForm(forms.ModelForm):
	class Meta:
		model = DealerBanner
		fields = ('title', 'image', 'flash', 'width', 'height', 'site', 'is_active', 'sort')
		
#Категории дилера	
class DealerAccountCategoryAddForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = ('title', 'is_active', 'sort')

#Информация дилера	
class DealerAccountCategoryInfoSearchForm(forms.Form):
	keyword = forms.CharField(max_length=100, label=_("keyword"))
		
#Информация дилера	
class DealerAccountCategoryInfoAddForm(forms.ModelForm):
	class Meta:
		model = CategoryItem
		fields = ('text', 'is_only_town', 'is_only_brand', 'is_active')
		
class DealerAccountCategoryMainInfoAddForm(forms.ModelForm):
	class Meta:
		model = CategoryItem
		fields = ('text', 'f', 'i', 'o', 'npas', 'spas', 'rdate', 'is_only_town', 'is_only_brand', 'is_active')
		
#Сообщение дилера	
class DealerAccountMessageForm(forms.ModelForm):
	class Meta:
		model = DealerMessage
		fields = ('text',)