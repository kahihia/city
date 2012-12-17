#!/usr/bin/env python
import sys
import os.path

hg_root = os.path.abspath(
  os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..' ))

venv_root = os.path.join(hg_root, 'venv')

ALLDIRS = [ hg_root,
            os.path.join(hg_root, 'alpha'),
            os.path.join(venv_root, 'lib', 'python2.6'), 
            os.path.join(venv_root, 'lib', 'python2.6', 'site-packages')
            ]

import site 

# Remember original sys.path.
prev_sys_path = list(sys.path) 

# Add each new site-packages directory.
for directory in ALLDIRS:
  site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
new_sys_path = [] 
for item in list(sys.path): 
    if item not in prev_sys_path: 
        new_sys_path.append(item) 
        sys.path.remove(item) 
sys.path[:0] = new_sys_path 

os.environ['DJANGO_SETTINGS_MODULE'] = 'alpha.settings_prod'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
