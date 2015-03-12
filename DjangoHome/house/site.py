#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from house.models import SystemStatus

logger = logging.getLogger(__name__)

from django.conf import settings as _settings
def settings(request):
    """
    TEMPLATE_CONTEXT_PROCESSORS
    """
    context = { 'settings': _settings }
    user = request.user
    try:
        #..... 这里设置全局变量
        system_status = SystemStatus.objects.all()[0]
        context['system_status'] = system_status
        context['site_name'] = '柠檬House'
        logger.info("set system status variable")
    except Exception,e:
        logger.error("settings:%s" % e)
    return context
