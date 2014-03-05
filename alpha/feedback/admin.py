from django.contrib import admin
from .models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'time')

admin.site.register(Feedback, FeedbackAdmin)
