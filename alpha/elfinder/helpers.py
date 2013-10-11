# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def get_module_class(class_path):
    """
    imports and returns module class from ``path.to.module.Class``
    argument
    """
    try:
        mod_name, cls_name = class_path.rsplit('.', 1)
        mod = import_module(mod_name)
    except ImportError, e:
        raise ImproperlyConfigured(('Error importing module %s: "%s"' %
                                   (mod_name, e)))
    return getattr(mod, cls_name)
