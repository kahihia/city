from django.contrib import admin
from models import VenueProfile
from image_cropping import ImageCroppingMixin

class VenueProfileAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ['name','cv_phone', 'cv_fax', 'cv_email', 'created_at', 'updated_at']
    date_hierarchy = 'updated_at'
    filter_vertical = ['cv_user']
    prepopulated_fields = {'cv_slug' : ('name',)}
    
admin.site.register(VenueProfile, VenueProfileAdmin)