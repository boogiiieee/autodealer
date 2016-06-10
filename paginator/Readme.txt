from django.views.generic.list_detail import object_list

PAGINATE_BY = 2

def portfolio(request, paginate_by=PAGINATE_BY):
	items = PortfolioPhoto.objects.filter(is_active=True)
	
	page = 1
	if request.method == 'GET':
		if 'page' in request.GET:
			page = int(request.GET.get('page'))
	
	return object_list(
		request = request,
		queryset = items,
		paginate_by = int(paginate_by),
		page = page,
		template_name = 'portfolio.html',
		template_object_name = 'objects',
		extra_context = {
			'href': u'/portfolio/',
			'flatpage':get_flat_page(request),
		}
	)