# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from pymorphy import get_morph

register = template.Library()
morph = get_morph(settings.PYMORPHY_DICTS['ru']['dir'])

@register.filter
def plural_from_object(source, object):
	l = len(object[0])
	if 1 == l:
		return source
	return morph.pluralize_inflected_ru(source.upper(), l).lower()