# -*- coding: utf-8 -*-

from django import forms
from captcha.fields import CaptchaField
from django.utils.translation import ugettext_lazy as _
import re

from feedback.models import Item as Items

class ItemForm(forms.ModelForm):
	captcha = CaptchaField()
	
	class Meta:
		model = Items
		fields = ('name','email','phone','text')
		
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
		
	def clean_phone(self): 
		phone = self.cleaned_data['phone']
		r = re.compile('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
		if not r.findall(phone):
			raise forms.ValidationError(_("Invalid phone field"))
		return phone
		
	def clean_text(self): 
		text = self.cleaned_data['text']
		if len(text) < 10:
			raise forms.ValidationError(_("Invalid text field"))
		return text
		
class OrderForm(ItemForm):
	class Meta:
		model = Items
		fields = ('name','email','phone')
		
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
		
	def clean_phone(self): 
		phone = self.cleaned_data['phone']
		r = re.compile('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
		if not r.findall(phone):
			raise forms.ValidationError(_("Invalid phone field"))
		return phone