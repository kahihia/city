# -*- coding: utf-8 -*-
from elfinder.conf import settings as elfinder_settings
from elfinder.helpers import get_module_class


def get_volume_driver():
    return get_module_class(elfinder_settings.ELFINDER_VOLUME_DRIVER)
