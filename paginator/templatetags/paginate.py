# -*- coding: utf-8 -*-

from django.template.base import Node, NodeList, Template, Context, Variable
from django import template
import re

register = template.Library()

class paginate_split_list_node(Node):
	def __init__(self, page_range, page):
		self.page_range = template.Variable(page_range)
		self.page = template.Variable(page)

	def render(self, context):
		page_range = self.page_range.resolve(context)
		page = self.page.resolve(context)
		page_count = len(page_range)
		
		if page_count > 10:
			if page < 5 or page > page_count-5:
				new_page_range = [[page_range[:5],True], [page_range[-5:],False]]
			else:
				new_page_range = [[page_range[:3],True], [page_range[page-2:page+1],True], [page_range[-3:],False]]
		else:
			new_page_range = [[page_range],False]

		context['paginate_page_range'] = new_page_range
		return ''
		
def paginate_split_list(parser, token):
	bits = list(token.split_contents())
	if len(bits) != 3:
		raise TemplateSyntaxError("%r takes < 3 arguments" % bits[0])
	return paginate_split_list_node(bits[1], bits[2])
	
paginate_split_list = register.tag(paginate_split_list)