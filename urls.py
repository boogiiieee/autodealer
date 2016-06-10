from django.conf.urls.defaults import *
from django.contrib.auth import views as auth_views
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^admin/filebrowser/', include('filebrowser.urls')),
	url(r'^tinymce/', include('tinymce.urls')),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^admin_tools/', include('admin_tools.urls')),
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
	url(r'^captcha/', include('captcha.urls')),
	
	url(r'^', include('project.urls')),
	
	url(r'^login/$', auth_views.login),
	url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='auth_logout'),
	url(r'^password/reset/$', 'django.contrib.auth.views.password_reset', {'template_name':'registration/passwd_reset_form.html',} ),
	url(r'^password/reset/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name':'registration/passwd_reset_done.html',} ),
	url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name':'registration/passwd_reset_confirm.html',} ),
	url(r'^password/reset/complete/$', 'django.contrib.auth.views.password_reset_complete', {'template_name':'registration/passwd_reset_complete.html',} ),
)