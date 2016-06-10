# -*- coding: utf-8 -*-

from django_ipgeobase.models import IPGeoBase
from project.models import Town
	
#######################################################################################################################
#######################################################################################################################

#Добавляет в request town
class TownMiddleware(object):
	def process_request(self, request):
		town = None
		if not 'town' in request.COOKIES:
			#ipgeobases = IPGeoBase.objects.by_ip('2.94.176.10')
			ipgeobases = IPGeoBase.objects.by_ip(request.META['REMOTE_ADDR'])
			if ipgeobases.exists():
				ipgeobase = ipgeobases[0]
				try: town = Town.objects.get(is_active=True, title=ipgeobase.city)
				except:
					try: town = Town.objects.filter(is_active=True, is_default=True)[0]
					except: pass
		else:
			try: town_id = int(request.COOKIES['town'])
			except ValueErrors:
				try: town = Town.objects.filter(is_active=True, is_default=True)[0]
				except: pass
			else:
				try: town = Town.objects.get(id=town_id)
				except:
					try: town = Town.objects.filter(is_active=True, is_default=True)[0]
					except: pass
				
		request.town = town
		
	def process_response(self, request, response):
		if not 'town' in request.COOKIES:
			#ipgeobases = IPGeoBase.objects.by_ip('2.94.176.10')
			ipgeobases = IPGeoBase.objects.by_ip(request.META['REMOTE_ADDR'])
			if ipgeobases.exists():
				ipgeobase = ipgeobases[0]
				try: town = Town.objects.get(title=ipgeobase.city)
				except: pass
				else:
					response.set_cookie("town", str(town.id), path="/")
					request.__class__.town = town
		else:
			try: town_id = int(request.COOKIES['town'])
			except ValuesError:
				try: town = Town.objects.filter(is_active=True, is_default=True)[0]
				except: pass
				else:
					response.set_cookie("town", str(town.id), path="/")
					request.__class__.town = town
		return response
		
#######################################################################################################################
#######################################################################################################################