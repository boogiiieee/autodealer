# -*- coding: utf-8 -*-

from django import template
import re

register = template.Library()
	
@register.filter(name='new_messages')
def new_messages(dealer, ds):
	return dealer.new_messages(ds).count()
	
@register.filter(name='get_count_dealers_in_town')
def get_count_dealers_in_town(brand, town):
	if town:
		return brand.get_dealers().filter(town__id=town.id).count()
	else:
		return brand.get_dealers().count()