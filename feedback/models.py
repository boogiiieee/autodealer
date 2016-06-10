# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce import models as TinymceField

from project.models import Dealer

class Item(models.Model):
	dealer = models.ForeignKey(Dealer, verbose_name=_("dealer"), blank=True, null=True)
	name = models.CharField(max_length=100, verbose_name=_("name"), blank=True)
	email = models.CharField(max_length=100, verbose_name=_("email"), blank=True)
	phone = models.CharField(max_length=100, verbose_name=_("phone"), blank=True)
	text = TinymceField.HTMLField(max_length=1000, verbose_name=_("text"))
	date = models.DateTimeField(verbose_name=_("date"), auto_now = True, auto_now_add = True)
	
	def __unicode__(self):
		return u'%s' % self.name
		
	class Meta: 
		verbose_name = _("feedback_item") 
		verbose_name_plural = _("feedback_items")
		ordering = ['-date']