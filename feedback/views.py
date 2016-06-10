from django.shortcuts import render_to_response
from django.template import RequestContext, loader, RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
import datetime
import settings

from feedback.models import Item as Items
from feedback.forms import ItemForm

def feedbackviews(request, template, sendmail=True, extra_context=None, context_processors=None, template_loader=loader):
	if request.method == 'POST':
		i = Items(date=datetime.datetime.now())
		form = ItemForm(request.POST, instance=i)
		if form.is_valid():
			form.save()

			current_site = Site.objects.get_current()

			if sendmail:
				send_mail(
					_('New item in %(domain)s.') % {'domain': current_site.domain},
					_(
						'Name:   %(name)s\nE-mail: %(email)s\nPhone:  %(phone)s\n\nText:   %(text)s\n\nLink: http://%(domain)s/feedback/%(id)d/\n\nAuto send message.'
					) % {
						'name': i.name,
						'email': i.email,
						'phone': i.phone,
						'text': i.text,
						'domain': current_site.domain,
						'id': i.id,
					},
					i.email,
					[a[1] for a in settings.MANAGERS],					
				)
			messages.add_message(request, messages.INFO, _("Thanks question send"))
			form = ItemForm()
	else:
		form = ItemForm()
		
	c = RequestContext(request, {'form':form}, context_processors)
	
	for key, value in extra_context.items():
		if callable(value):
			c[key] = value()
		else:
			c[key] = value
			
	t = template_loader.get_template(template)
	return HttpResponse(t.render(c))