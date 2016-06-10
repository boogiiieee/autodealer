# -*- coding: utf-8 -*-

import os
from django.conf import settings

PAGINATE_BY = getattr(settings, 'PROJECT_PAGINATE_BY', 25)