from django.conf.urls import *

from ajaxuploader.views import AjaxFileUploader
from ajaxuploader.backends.default_storage import DefaultStorageUploadBackend


default_storage_uploader = AjaxFileUploader(backend=DefaultStorageUploadBackend)

urlpatterns = patterns('',
    url(r'^upload$', default_storage_uploader, name="ajax-upload-default-storage"),                
)
