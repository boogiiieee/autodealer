# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseBadRequest, HttpResponseRedirect, HttpResponse, Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import list_detail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Avg, Count
from django.contrib import messages
from django.contrib import auth
from django.db.models import Q
import datetime
import pickle
import settings

from project.models import Town, Brand, Dealer, DealerSeance, DealerBanner, DealerBlog, DealerComment, DealerMessage, Category, CategoryItem, Bookmark, Partner
from project.forms import DealerSearchForm, DealerCommentForm, DealerAccountLicenseForm, DealerAccountForm, DealerAccountBlogAddForm, DealerAccountBlogAddFormset, DealerAccountBannerAddForm, DealerAccountCategoryAddForm, DealerAccountCategoryInfoSearchForm, DealerAccountCategoryInfoAddForm, DealerAccountCategoryMainInfoAddForm, DealerAccountMessageForm
from project.conf import settings as conf
from feedback.views import feedbackviews

#######################################################################################################################
#######################################################################################################################

def how_registration(request):
	return feedbackviews(
		request = request,
		template = 'how_registration.html',
		extra_context = {'a':4},
	)
	
def information(request):
	return feedbackviews(
		request = request,
		template = 'information.html',
		extra_context = {'a':5},
	)
	
def contacts(request):
	return feedbackviews(
		request = request,
		template = 'contacts.html',
		extra_context = {'a':7},
	)

#######################################################################################################################
#######################################################################################################################

@login_required
def for_dealers(request):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		cs = Category.objects.filter(is_active=True).order_by('title')
		
		if cs.count() > 0:
			if cs.count() < 3: rcs = {'col1':cs, 'col2':None, 'col3':None}
			elif cs.count() >= 3:
				step = cs.count() / 3
				rcs = {
					'col1':cs[0:step],
					'col2':cs[step:2*step],
					'col3':cs[2*step:],
				}
		else: rcs = None
		
		siform = DealerAccountCategoryInfoSearchForm()
		return render_to_response('for_dealers/for_dealers.html', {'a':2, 'siform':siform, 'items':rcs}, RequestContext(request))
	
@login_required
def for_dealers_info(request, id, slug):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: cs = Category.objects.get(id=id, is_active=True)
		except: raise Http404()
		else:	
			dsic = CategoryItem.objects.filter(is_active=True, category=cs)
			for ic in dsic:
				if ic.is_only_town:
					if not Dealer.objects.filter(
						user=request.user, is_banned=False, is_active=True,
						town__id__in=[tw.id for tw in ic.dealer.town.filter(is_active=True)]
					).count(): dsic = dsic.exclude(id=ic.id)
				if ic.is_only_brand:
					if not Dealer.objects.filter(
						user=request.user, is_banned=False, is_active=True,
						brand__id__in=[br.id for br in ic.dealer.brand.filter(is_active=True)]
					).count(): dsic = dsic.exclude(id=ic.id)
					
			siform = DealerAccountCategoryInfoSearchForm()
			
			return list_detail.object_list(
				request,
				queryset = dsic,
				paginate_by = conf.PAGINATE_BY,
				page = page,
				template_name = 'for_dealers/for_dealers_info.html',
				template_object_name = 'dsic',
				extra_context = {
					'a':2, 'siform':siform, 'ds':ds, 'cs':cs,
				},
			)
	
@login_required
def for_dealers_search(request):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		dsic = CategoryItem.objects.filter(is_active=True)

		siform = DealerAccountCategoryInfoSearchForm(request.GET)
		if siform.is_valid():
			cd = siform.cleaned_data
			if 'keyword' in cd and cd['keyword']:
				dsic = dsic.filter(
					Q(text__icontains=cd['keyword']) |
					Q(f__icontains=cd['keyword']) |
					Q(i__icontains=cd['keyword']) |
					Q(o__icontains=cd['keyword']) |
					Q(npas__icontains=cd['keyword']) |
					Q(spas__icontains=cd['keyword'])
				)
		
		return list_detail.object_list(
			request,
			queryset = dsic,
			paginate_by = conf.PAGINATE_BY,
			page = page,
			template_name = 'for_dealers/search.html',
			template_object_name = 'dsic',
			extra_context = {
				'a':2, 'siform':siform, 'ds':ds,
			},
		)
	
#######################################################################################################################
#######################################################################################################################

def feedback(request):
	return feedbackviews(
		request = request,
		template = 'feedback/feedback.html',
		extra_context = {},
	)

#######################################################################################################################
#######################################################################################################################

@login_required
def cabinet_in(request):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		DealerSeance.objects.create(dealer=ds, ip=request.META['REMOTE_ADDR'])
	return HttpResponseRedirect('/cabinet/')

#######################################################################################################################
#######################################################################################################################

def cabinet_proc(request):
	dss = None
	dsbnc = 0
	dsnm = 0
	
	if request.user.is_authenticated():
		dss = DealerSeance.objects.filter(dealer__user=request.user, dealer__is_banned=False, dealer__is_active=True)
		dsbnc = DealerComment.objects.filter(item__dealer__user=request.user, item__dealer__is_banned=False, item__dealer__is_active=True, is_active=False).count()
		dsnm = dsm = DealerMessage.objects.filter(fdealer__user=request.user, is_read=False).count()
	return {
		'seanses': dss,
		'new_comments': dsbnc,
		'new_messages': dsnm,
	}

@login_required
def cabinet_license(request):
	try: ds = Dealer.objects.get(user=request.user, is_license=False, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if request.method == 'POST':
			aform = DealerAccountLicenseForm(request.POST, instance=ds)
			if aform.is_valid():
				aform.save()
				messages.add_message(request, messages.INFO, _("You can use all site's function"))
				return HttpResponseRedirect('/cabinet/')
		else:
			aform = DealerAccountLicenseForm()
			
		return render_to_response('cabinet/license.html', {'a':3, 'aform':aform}, RequestContext(request, processors=[cabinet_proc]))

@login_required
def cabinet(request):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if request.method == 'POST':
			aform = DealerAccountForm(request.POST, request.FILES, instance=ds)
			if aform.is_valid():
				aform.save()
				messages.add_message(request, messages.INFO, _("Profile's data saved"))
				aform = DealerAccountForm(instance=ds)
		else:
			aform = DealerAccountForm(instance=ds)
		return render_to_response('cabinet/cabinet.html', {'a':3, 'a1':1, 'ds':ds, 'aform':aform}, RequestContext(request, processors=[cabinet_proc]))
		
@login_required
def cabinet_passwd(request):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if request.method == 'POST':
			aform = PasswordChangeForm(user=request.user, data=request.POST)
			if aform.is_valid():
				aform.save()
				messages.add_message(request, messages.INFO, _("New password saved"))
				aform = PasswordChangeForm(user=request.user, data=request.POST)
		else:
			aform = PasswordChangeForm(request.user)
		return render_to_response('cabinet/passwd.html', {'a':3, 'a1':2, 'aform':aform}, RequestContext(request, processors=[cabinet_proc]))
		
@login_required
def cabinet_pay(request):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		return render_to_response('cabinet/pay.html', {'a':3, 'a1':3}, RequestContext(request, processors=[cabinet_proc]))
		
@login_required
def cabinet_blog(request):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		dsb = DealerBlog.objects.filter(dealer=ds)
		
		return list_detail.object_list(
			request,
			queryset = dsb,
			paginate_by = conf.PAGINATE_BY,
			page = page,
			template_name = 'cabinet/blog.html',
			template_object_name = 'dsb',
			extra_context = {
				'a':3,
				'a1':4,
			},
			context_processors = [cabinet_proc],
		)
		
@login_required
def cabinet_blog_add(request):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		if request.method == 'POST':
			dsb = DealerBlog(dealer=ds)
			aform = DealerAccountBlogAddForm(request.POST, instance=dsb)
			if aform.is_valid():
				aform.save()
				messages.add_message(request, messages.INFO, _("Blog's item saved"))
				return HttpResponseRedirect(dsb.get_admin_url())
		else:
			aform = DealerAccountBlogAddForm()
		return render_to_response('cabinet/blog_add.html', {'a':3, 'a1':4, 'aform':aform}, RequestContext(request, processors=[cabinet_proc]))
		
@login_required
def cabinet_blog_edit(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsb = DealerBlog.objects.get(id=id, dealer=ds)
		except: raise Http404()
		else:
			if request.method == 'POST':
				aform = DealerAccountBlogAddForm(request.POST, instance=dsb)
				aformset = DealerAccountBlogAddFormset(request.POST, instance=dsb)
				if aform.is_valid() and aformset.is_valid():
					aform.save()
					aformset.save()
					messages.add_message(request, messages.INFO, _("Blog's item saved"))
					aform = DealerAccountBlogAddForm(instance=dsb)
					aformset = DealerAccountBlogAddFormset(instance=dsb)
				else:
					messages.add_message(request, messages.INFO, _("Blog's item error saved"))
			else:
				aform = DealerAccountBlogAddForm(instance=dsb)
				aformset = DealerAccountBlogAddFormset(instance=dsb)

			return render_to_response('cabinet/blog_edit.html', {'a':3, 'a1':4, 'aform':aform, 'aformset':aformset, 'dsb':dsb}, RequestContext(request, processors=[cabinet_proc]))

@login_required
def cabinet_blog_del(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsb = DealerBlog.objects.get(id=id, dealer=ds)
		except: raise Http404()
		else:
			dsb.delete()
			messages.add_message(request, messages.INFO, _("Blog's item deleted"))
			return HttpResponseRedirect('/cabinet/blog/')
			
@login_required
def cabinet_banner(request):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		dsbb = DealerBanner.objects.filter(dealer=ds)
		
		return list_detail.object_list(
			request,
			queryset = dsbb,
			paginate_by = conf.PAGINATE_BY,
			page = page,
			template_name = 'cabinet/banner.html',
			template_object_name = 'dsbb',
			extra_context = {
				'a':3,
				'a1':5,
			},
			context_processors = [cabinet_proc],
		)
		
@login_required
def cabinet_banner_add(request):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		if request.method == 'POST':
			dsbb = DealerBanner(dealer=ds)
			aform = DealerAccountBannerAddForm(request.POST, request.FILES, instance=dsbb)
			if aform.is_valid():
				aform.save()
				messages.add_message(request, messages.INFO, _("Banner saved"))
				return HttpResponseRedirect(dsbb.get_admin_url())
		else:
			aform = DealerAccountBannerAddForm()
			
		return render_to_response('cabinet/banner_add.html', {'a':3, 'a1':5, 'aform':aform}, RequestContext(request, processors=[cabinet_proc]))
		
@login_required
def cabinet_banner_edit(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsbb = DealerBanner.objects.get(id=id, dealer=ds)
		except: raise Http404()
		else:
			if request.method == 'POST':
				aform = DealerAccountBannerAddForm(request.POST, request.FILES, instance=dsbb)
				if aform.is_valid():
					aform.save()
					messages.add_message(request, messages.INFO, _("Banner saved"))
					aform = DealerAccountBannerAddForm(instance=dsbb)
			else:
				aform = DealerAccountBannerAddForm(instance=dsbb)
				
			return render_to_response('cabinet/banner_edit.html', {'a':3, 'a1':5, 'aform':aform, 'dsbb':dsbb}, RequestContext(request, processors=[cabinet_proc]))

@login_required
def cabinet_banner_del(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsbb = DealerBanner.objects.get(id=id, dealer=ds)
		except: raise Http404()
		else:
			dsbb.delete()
			messages.add_message(request, messages.INFO, _("Banner deleted"))
			return HttpResponseRedirect('/cabinet/bb/')
			
@login_required
def cabinet_for_dealer(request):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		dsc = Category.objects.filter(Q(is_active=True) | Q(dealer=ds))

		return list_detail.object_list(
			request,
			queryset = dsc,
			paginate_by = conf.PAGINATE_BY,
			page = page,
			template_name = 'cabinet/for_dealer.html',
			template_object_name = 'dsc',
			extra_context = {
				'a':3,
				'a1':6,
				'ds':ds,
			},
			context_processors = [cabinet_proc],
		)
		
@login_required
def cabinet_for_dealer_add(request):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		if request.method == 'POST':
			dsc = Category(dealer=ds)
			aform = DealerAccountCategoryAddForm(request.POST, instance=dsc)
			if aform.is_valid():
				aform.save()
				messages.add_message(request, messages.INFO, _("Category saved"))
				return HttpResponseRedirect('/cabinet/for-dealer/edit/%d/' % dsc.id)
		else:
			aform = DealerAccountCategoryAddForm()
			
		return render_to_response('cabinet/for_dealer_add.html', {'a':3, 'a1':6, 'aform':aform}, RequestContext(request, processors=[cabinet_proc]))
			
@login_required
def cabinet_for_dealer_edit(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsc = Category.objects.get(id=id, dealer=ds)
		except: raise Http404()
		else:
			if request.method == 'POST':
				aform = DealerAccountCategoryAddForm(request.POST, instance=dsc)
				if aform.is_valid():
					aform.save()
					messages.add_message(request, messages.INFO, _("Category saved"))
					aform = DealerAccountCategoryAddForm(instance=dsc)
			else:
				aform = DealerAccountCategoryAddForm(instance=dsc)
				
			return render_to_response('cabinet/for_dealer_edit.html', {'a':3, 'a1':6, 'aform':aform, 'dsc':dsc}, RequestContext(request, processors=[cabinet_proc]))

@login_required
def cabinet_for_dealer_del(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsc = Category.objects.get(id=id, dealer=ds)
		except: raise Http404()
		else:
			if dsc.get_items().count() > 0:
				messages.add_message(request, messages.INFO, _("Category don't deleted. Category not empty."))
			else:
				dsc.delete()
				messages.add_message(request, messages.INFO, _("Category deleted"))
			return HttpResponseRedirect('/cabinet/for-dealer/')
			
@login_required
def cabinet_for_dealer_bookmark(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsc = Category.objects.get(id=id, is_active=True)
		except: raise Http404()
		else:
			Bookmark.objects.get_or_create(dealer=ds, category=dsc)
			messages.add_message(request, messages.INFO, _("Category %s added in bookmark") % dsc.title)
			if 'HTTP_REFERER' in request.META: ref = request.META['HTTP_REFERER']
			else: ref = '/cabinet/partner/'
			return HttpResponseRedirect(ref)
			
@login_required
def cabinet_for_dealer_info(request, id):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsc = Category.objects.get(Q(id=id) & (Q(is_active=True) | Q(dealer=ds)))
		except: raise Http404()
		else:
			dsic = CategoryItem.objects.filter(Q(category=dsc) & (Q(is_active=True) | Q(dealer=ds)))
			for ic in dsic:
				if ic.is_only_town:
					if not Dealer.objects.filter(
						user=request.user, is_banned=False, is_active=True,
						town__id__in=[tw.id for tw in ic.dealer.town.filter(is_active=True)]
					).count(): dsic = dsic.exclude(id=ic.id)
				if ic.is_only_brand:
					if not Dealer.objects.filter(
						user=request.user, is_banned=False, is_active=True,
						brand__id__in=[br.id for br in ic.dealer.brand.filter(is_active=True)]
					).count(): dsic = dsic.exclude(id=ic.id)

			return list_detail.object_list(
				request,
				queryset = dsic,
				paginate_by = conf.PAGINATE_BY,
				page = page,
				template_name = 'cabinet/for_dealer_info.html',
				template_object_name = 'dsic',
				extra_context = {
					'a':3,
					'a1':6,
					'ds':ds,
					'dsc':dsc
				},
				context_processors = [cabinet_proc],
			)
			
@login_required
def cabinet_for_dealer_info_add(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsc = Category.objects.get(Q(id=id) & (Q(is_active=True) | Q(dealer=ds)))
		except: raise Http404()
		else:
			if dsc.is_main: F = DealerAccountCategoryMainInfoAddForm
			else: F = DealerAccountCategoryInfoAddForm
			
			if request.method == 'POST':
				dsci = CategoryItem(dealer=ds, category=dsc)
				aform = F(request.POST, instance=dsci)
				if aform.is_valid():
					aform.save()
					messages.add_message(request, messages.INFO, _("Category's item saved"))
					return HttpResponseRedirect('/cabinet/for-dealer/%d/edit/%d/' % (dsc.id, dsci.id))
			else:
				aform = F()
			
		return render_to_response('cabinet/for_dealer_info_add.html', {'a':3, 'a1':6, 'dsc':dsc, 'aform':aform}, RequestContext(request, processors=[cabinet_proc]))
	
@login_required
def cabinet_for_dealer_info_edit(request, cid, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsc = Category.objects.get(Q(id=cid) & (Q(is_active=True) | Q(dealer=ds)))
		except: raise Http404()
		else:
			try: dsci = CategoryItem.objects.get(id=id)
			except: raise Http404()
			else:
				if dsc.is_main: F = DealerAccountCategoryMainInfoAddForm
				else: F = DealerAccountCategoryInfoAddForm
			
				if request.method == 'POST':
					aform = F(request.POST, instance=dsci)
					if aform.is_valid():
						aform.save()
						messages.add_message(request, messages.INFO, _("Category's item saved"))
						aform = F(instance=dsci)
				else:
					aform = F(instance=dsci)
					
				return render_to_response('cabinet/for_dealer_info_edit.html', {'a':3, 'a1':6, 'aform':aform, 'dsc':dsc, 'dsci':dsci}, RequestContext(request, processors=[cabinet_proc]))
		
@login_required
def cabinet_for_dealer_info_del(request, cid, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		if not ds.is_license: return HttpResponseRedirect('/cabinet/license/')
		
		try: dsc = Category.objects.get(id=cid)
		except: raise Http404()
		else:
			try: dsci = CategoryItem.objects.get(id=id)
			except: raise Http404()
			else:
				dsci.delete()
				messages.add_message(request, messages.INFO, _("Category's item deleted"))
				return HttpResponseRedirect('/cabinet/for-dealer/%d/' % dsc.id)
				
@login_required
def cabinet_bookmark(request):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		dsbm = Bookmark.objects.filter((Q(category__is_active=True) | Q(category__dealer=ds)) & Q(dealer=ds))

		return list_detail.object_list(
			request,
			queryset = dsbm,
			paginate_by = conf.PAGINATE_BY,
			page = page,
			template_name = 'cabinet/bookmark.html',
			template_object_name = 'dsbm',
			extra_context = {
				'a':3,
				'a1':7,
				'ds':ds,
				'dsbm':dsbm
			},
			context_processors = [cabinet_proc],
		)
		
@login_required
def cabinet_bookmark_del(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		try: dsbm = Bookmark.objects.get(id=id)
		except: raise Http404()
		else:
			dsbm.delete()
			messages.add_message(request, messages.INFO, _("Bookmark deleted"))
			return HttpResponseRedirect('/cabinet/bookmark/')
			
@login_required
def cabinet_partner(request):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		dsp = Partner.objects.filter(dealer=ds)
		return render_to_response('cabinet/partner.html', {'a':3, 'a1':8, 'dsp_list':dsp}, RequestContext(request, processors=[cabinet_proc]))

@login_required
def cabinet_partner_add(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		try: pds = Dealer.objects.get(id=id, is_banned=False, is_active=True)
		except: raise Http404()
		else:
			Partner.objects.get_or_create(dealer=ds, pdealer=pds)
			messages.add_message(request, messages.INFO, _("Dealer %s added in partners") % pds.title)
			if 'HTTP_REFERER' in request.META: ref = request.META['HTTP_REFERER']
			else: ref = '/cabinet/partner/'
			return HttpResponseRedirect(ref)
			
@login_required
def cabinet_partner_del(request, id):
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		try: pds = Partner.objects.get(id=id, dealer=ds)
		except: raise Http404()
		else:
			pds.delete()
			messages.add_message(request, messages.INFO, _("Partner deleted"))
			return HttpResponseRedirect('/cabinet/partner/')
		
@login_required
def cabinet_messages(request):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		dsmg = DealerMessage.objects.filter(Q(dealer=ds) | Q(fdealer=ds))
		dsm_ids = [d['dealer'] for d in dsmg.values('dealer')] + [d['fdealer'] for d in dsmg.values('fdealer')]
		dsm_ids = list(set(dsm_ids))
			
		dsm = Dealer.objects.filter(id__in=dsm_ids).exclude(user=request.user)

		return list_detail.object_list(
				request,
				queryset = dsm,
				paginate_by = conf.PAGINATE_BY,
				page = page,
				template_name = 'cabinet/messages.html',
				template_object_name = 'dsm',
				extra_context = {
					'a':3,
					'a1':9,
					'ds':ds,
				},
				context_processors = [cabinet_proc],
			)
			
@login_required
def cabinet_message(request, id):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try: ds = Dealer.objects.get(user=request.user, is_banned=False, is_active=True)
	except: raise Http404()
	else:
		try: pds = Dealer.objects.get(id=id, is_banned=False, is_active=True)
		except: raise Http404()
		else:
			dsm = DealerMessage.objects.filter(
				(Q(dealer=ds) & Q(fdealer=pds)) | (Q(dealer=pds) & Q(fdealer=ds))
			)
			dsm.filter(fdealer=ds).update(is_read=True)
			
			idsm = DealerMessage(dealer=ds, fdealer=pds)
			if request.method == 'POST':
				aform = DealerAccountMessageForm(request.POST, instance=idsm)
				if aform.is_valid():
					aform.save()
					messages.add_message(request, messages.INFO, _("Message sent"))
					aform = DealerAccountMessageForm()
			else:
				aform = DealerAccountMessageForm()

			return list_detail.object_list(
				request,
				queryset = dsm,
				paginate_by = conf.PAGINATE_BY,
				page = page,
				template_name = 'cabinet/message.html',
				template_object_name = 'dsm',
				extra_context = {
					'a':3,
					'a1':9,
					'ds':ds,
					'pds':pds,
					'aform':aform,
				},
				context_processors = [cabinet_proc],
			)
			
#######################################################################################################################
#######################################################################################################################

def brands(request):
	bs = Brand.objects.filter(is_active=True).order_by('title')
	for b in bs:
		if not b.get_count_dealers():
			bs = bs.exclude(id=b.id)
	
	if bs.count() < 3: brands = {'col1':bs, 'col2':None, 'col3':None}
	elif bs.count() >= 3:
		step = bs.count() / 3
		brands = {
			'col1':bs[0:step],
			'col2':bs[step:2*step],
			'col3':bs[2*step:],
		}
	return render_to_response('dealers/brands.html', {'a':1, 'items':brands}, RequestContext(request))
	
#######################################################################################################################
#######################################################################################################################

def dealers(request, slug):
	try: bs = Brand.objects.get(is_active=True, slug=slug)
	except Brand.DoesNotExist: raise Http404()
	else:
		ds = bs.dealers.filter(is_banned=False, is_active=True).order_by('title')
		
		if request.town:
			ds = ds.filter(town__id=request.town.id)
	
		if ds.count() > 0:
			if ds.count() < 3: dls = {'col1':ds, 'col2':None, 'col3':None}
			elif ds.count() >= 3:
				step = ds.count() / 3
				dls = {
					'col1':ds[0:step],
					'col2':ds[step:2*step],
					'col3':ds[2*step:],
				}
		else: dls = None
		
		banners = DealerBanner.objects.filter(is_active=True, dealer__in=ds, dealer__is_active=True, dealer__is_banned=False).order_by('?')[0:3]
		blogs = DealerBlog.objects.filter(is_active=True, dealer__in=ds, dealer__is_active=True, dealer__is_banned=False).order_by('?')[0:3]
		
		search_initial = {'brand':bs,}
		if request.town: search_initial = {'brand':bs, 'town':request.town}
		sform = DealerSearchForm(initial=search_initial)
		
		return render_to_response('dealers/dealers.html', {
			'a':1, 'items':dls, 'brand':bs, 'banners':banners, 'blogs':blogs, 'sform':sform
		}, RequestContext(request))

#######################################################################################################################
#######################################################################################################################

def dealer(request, id, slug, bid=None):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try:
		if bid: bs = Brand.objects.get(is_active=True, id=bid)
		else: bs = None
	except Brand.DoesNotExist: raise Http404()
	
	try: ds = Dealer.objects.get(id=id, is_banned=False, is_active=True)
	except Dealer.DoesNotExist: raise Http404()
	
	banners = DealerBanner.objects.filter(is_active=True, dealer__in=[ds], dealer__is_active=True, dealer__is_banned=False).order_by('?')[0:3]
	ablogs = DealerBlog.objects.filter(is_active=True, dealer__in=[ds], dealer__is_active=True, dealer__is_banned=False)
	blogs = ablogs.all().order_by('?')[0:3]
	search_initial = {'brand':bs,}
	if request.town: search_initial = {'brand':bs, 'town':request.town}
	sform = DealerSearchForm(initial=search_initial)
	
	return list_detail.object_list(
		request,
		queryset = ablogs,
		paginate_by = conf.PAGINATE_BY,
		page = page,
		template_name = 'dealers/dealer.html',
		template_object_name = 'blogs',
		extra_context = {
			'a':1,
			'brand':bs,
			'dealer':ds,
			'banners':banners,
			'blogs':blogs,
			'sform':sform,
		},
	)

#######################################################################################################################
#######################################################################################################################

def blog(request, id, slug):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
		
	try: bb = DealerBlog.objects.get(id=id, is_active=True)
	except DealerBlog.DoesNotExist: raise Http404()
	
	bc = bb.get_comments()
	
	banners = DealerBanner.objects.filter(is_active=True, dealer__in=[bb.dealer], dealer__is_active=True, dealer__is_banned=False).order_by('?')[0:3]
	blogs = DealerBlog.objects.filter(is_active=True, dealer__in=[bb.dealer], dealer__is_active=True, dealer__is_banned=False).order_by('?')[0:3]
	search_initial = {}
	if request.town: search_initial = {'town':request.town}
	sform = DealerSearchForm(initial=search_initial)
	
	blog_user_data = None
	if request.method == 'POST' and bb:
		i = DealerComment(item=bb, date=datetime.datetime.now())
		bform = DealerCommentForm(request.POST, instance=i)
		if bform.is_valid():
			bform.save()
			messages.add_message(request, messages.INFO, _("Thanks letter send"))
			
			cd = bform.cleaned_data
			blog_user_data = pickle.dumps({
				'name':cd['name'],
				'phone':cd['phone'],
				'org':cd['org'],
				'post':cd['post'],
				'email':cd['email'],
			})
			
			initial = {}
			if 'blog_user_data' in request.COOKIES:
				initial = pickle.loads(request.COOKIES['blog_user_data'])
			bform = DealerCommentForm(initial=initial)
	else:
		initial = {}
		if 'blog_user_data' in request.COOKIES:
			initial = pickle.loads(request.COOKIES['blog_user_data'])
		bform = DealerCommentForm(initial=initial)
	
	response = list_detail.object_list(
		request,
		queryset = bc,
		paginate_by = conf.PAGINATE_BY,
		page = page,
		template_name = 'dealers/blog.html',
		template_object_name = 'comments',
		extra_context = {
			'a':1,
			'bform':bform,
			'blog':bb,
			'dealer':bb.dealer,
			'banners':banners,
			'blogs':blogs,
			'sform':sform,
		},
	)
	
	if blog_user_data:
		response.set_cookie("blog_user_data", blog_user_data)
	
	return response

#######################################################################################################################
#######################################################################################################################

def search(request):
	page = 1
	if 'page' in request.GET:
		try: page = int(request.GET.get('page'))
		except: raise Http404()
	
	ds = Dealer.objects.filter(is_banned=False, is_active=True)
	
	sform = DealerSearchForm(request.GET)
	if sform.is_valid():
		cd = sform.cleaned_data
		if 'title' in cd and cd['title']: ds = ds.filter(title__icontains=cd['title'])
		if 'town' in cd and cd['town']: ds = ds.filter(town__id=cd['town'].id)
		if 'brand' in cd and cd['brand']: ds = ds.filter(brand__id=cd['brand'].id)
		
	ds = ds.order_by('title')
	
	return list_detail.object_list(
		request,
		queryset = ds,
		paginate_by = conf.PAGINATE_BY,
		page = page,
		template_name = 'dealers/search.html',
		template_object_name = 'dealsers',
		extra_context = {
			'a':1,
			'sform':sform,
			'dealer':ds,
		},
	)

#######################################################################################################################
#######################################################################################################################

def change_town(request):
	tw = Town.objects.filter(is_active=True).order_by('title')
	
	if tw.count() < 3: ftowns = {'col1':tw, 'col2':None, 'col3':None}
	elif tw.count() >= 3:
		step = tw.count() / 3
		ftowns = {
			'col1':tw[0:step],
			'col2':tw[step:2*step],
			'col3':tw[2*step:],
		}
	
	response = render_to_response('dealers/change_town.html', {'towns_list':ftowns}, RequestContext(request))
	
	idd = None
	if 'i' in request.GET:
		try: id = int(request.GET.get('i'))
		except: raise Http404()
		else:
			try: tw = Town.objects.get(id=id, is_active=True)
			except: pass
			else:
				idd = tw.id
				messages.add_message(request, messages.INFO, _("Town %s changed") % tw.title)
				response = HttpResponseRedirect('/change-town/')
	
	if idd:
		response.set_cookie("town", str(idd), path="/")
	else:
		response = render_to_response('dealers/change_town.html', {'towns_list':ftowns}, RequestContext(request))
	
	return response
	
#######################################################################################################################
#######################################################################################################################