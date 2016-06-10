Перевод админки Dashboard на русский язык с учетом падежей, числа и т.д.
Для работы приложения нужен модуль pymorphy.

1) Скопировать приложение admintrans в корень проекта.
2) Скопировать шаблоны из приложения в папку templates в корне проекта.
3) Добавить в settings.py 'admintrans',
4) Заменить в dushboard.py:
	class CustomAppIndexDashboard(AppIndexDashboard):
		def __init__(self, *args, **kwargs):
			AppIndexDashboard.__init__(self, *args, **kwargs)

			self.children += [
				modules.ModelList(_(self.app_title), self.models),
5) Добавить в init.py каждого приложения:
	# -*- coding: utf-8 -*-
	from django.utils.translation import ugettext_lazy as _
	_('Имя приложения')
6) Добавить в файл admin.py приложения from admintrans.admin import *
7) Создать файл перевода для проекта и приложений