# -*- coding: utf-8 -*-

from project.models import Town, DealerBanner, DealerBlog
from project.forms import DealerSearchForm

##################################################################################################	
##################################################################################################

def custom_proc(request):
	search_initial = {}
	if request.town: search_initial = {'town':request.town}
		
	return {
		'towns': Town.objects.filter(is_active=True, is_main=True),
		'banners': DealerBanner.objects.filter(is_active=True, dealer__is_active=True, dealer__is_banned=False).order_by('?')[0:3],
		'blogs': DealerBlog.objects.filter(is_active=True, dealer__is_active=True, dealer__is_banned=False).order_by('?')[0:3],
		'sform': DealerSearchForm(initial=search_initial),
	}
	
##################################################################################################	
##################################################################################################