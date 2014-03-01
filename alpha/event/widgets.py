from django import forms
from django.conf import settings
from django.template import Template, Context
from django.utils.safestring import mark_safe
import json

from ckeditor.widgets import CKEditorWidget

STATIC_PREFIX = settings.STATIC_URL

from accounts.models import VenueAccount


class WhenWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super(WhenWidget, self).__init__(*args, **kwargs)
        #self.when_json = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):
        html = super(WhenWidget, self).render(name, value, *args, **kwargs)
        #html += self.when_json.render("when_json", "", {"id":'id_when_json'})
        return mark_safe(html)


class GeoCompleteWidget(forms.TextInput):
    def __init__(self, *args, **kw):
        super(GeoCompleteWidget, self).__init__(*args, **kw)
        self.geo_venue = forms.widgets.HiddenInput()
        self.geo_address = forms.widgets.HiddenInput()
        self.geo_street = forms.widgets.HiddenInput()
        self.geo_street_number = forms.widgets.HiddenInput()
        self.geo_city = forms.widgets.HiddenInput()
        self.geo_country = forms.widgets.HiddenInput()
        self.geo_longtitude = forms.widgets.HiddenInput()
        self.geo_latitude = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):
        if not value:
            value = {}
        html = super(GeoCompleteWidget, self).render(name, value.get('full', ''), *args, **kwargs)
        html += "<div class='geo-details'>"
        html += self.geo_venue.render("geo_venue", "", {"id": 'id_geo_venue', 'data-geo': "name", 'value': value.get('venue', '')})
        html += self.geo_address.render("geo_address", "", {"id": 'id_geo_address', 'data-geo': "formatted_address", 'value': value.get('venue', '')})
        html += self.geo_street.render("geo_street", "", {"id": 'id_geo_street', 'data-geo': "route", 'value': value.get('street', '')})
        html += self.geo_street_number.render("geo_street_number", "", {"id": 'id_geo_street_number', 'data-geo': "street_number", 'value': value.get('street_number', '')})
        html += self.geo_city.render("geo_city", "", {"id": 'id_geo_city', 'data-geo': "locality", 'value': value.get('city', '')})
        html += self.geo_country.render("geo_country", "", {"id": 'id_geo_country', 'data-geo': "country", 'value': value.get('country', '')})
        html += self.geo_longtitude.render("geo_longtitude", "", {"id": 'id_geo_longtitude', 'data-geo': "lng", 'value': value.get('longtitude', '')})
        html += self.geo_latitude.render("geo_latitude", "", {"id": 'id_geo_latitude', 'data-geo': "lat", 'value': value.get('latitude', '')})
        html += "</div>"
        return mark_safe(html)

    def value_from_datadict(self, data, files, name):
        return {
            "full": super(GeoCompleteWidget, self).value_from_datadict(data, files, name),
            "venue": self.geo_venue.value_from_datadict(data, files, 'geo_venue'),
            "street": self.geo_street.value_from_datadict(data, files, 'geo_street'),
            "city": self.geo_city.value_from_datadict(data, files, 'geo_city'),
            "country": self.geo_country.value_from_datadict(data, files, 'geo_country'),
            "longtitude": self.geo_longtitude.value_from_datadict(data, files, 'geo_longtitude'),
            "latitude": self.geo_latitude.value_from_datadict(data, files, 'geo_latitude')
        }

    def decompress(self, value):
        return json.loads(value)


class DescriptionWidget(CKEditorWidget):
    def __init__(self, *args, **kwargs):
        super(DescriptionWidget, self).__init__(*args, **kwargs)
        self.description_json = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):
       html = super(DescriptionWidget, self).render(name, value, *args, **kwargs)
       html += self.description_json.render("description_json", "", {"id":'id_description_json'})
       return mark_safe(html)

    class Media(object):
        js = (
            u'%sckeditor/ckeditor/ckeditor.js' % STATIC_PREFIX,
            u'%sjs/description.js' % STATIC_PREFIX            
        )


class AjaxCropWidget(forms.TextInput):
    class Media:
        js = (
            "image_cropping/js/jquery.Jcrop.min.js",
            "image_cropping/image_cropping.js",
            "%sjs/fileuploader.js" % STATIC_PREFIX,
            "%sjs/picture.js" % STATIC_PREFIX,
        )
        css = {'all': (
            "%simage_cropping/css/jquery.Jcrop.min.css" % STATIC_PREFIX,
            "%sajaxuploader/css/fileuploader.css" % STATIC_PREFIX,
        )}

    def __init__(self, *args, **kw):
        super(AjaxCropWidget, self).__init__(*args, **kw)
        self.picture_src = forms.widgets.HiddenInput()

    def value_from_datadict(self, data, files, name):
        return self.picture_src.value_from_datadict(data, files, 'picture_src')

    def render(self, name, value, *args, **kwargs):
        if value == "/media/":
            value = ""
        if value:
            html = self.picture_src.render("picture_src", "", {"id": 'id_picture_src', "value": "%s" % (value)})
        else:
            html = self.picture_src.render("picture_src", "", {"id": 'id_picture_src'})
        html += Template("""<div id="file-uploader" data-csrf-token="{{ csrf_token }}">
            <noscript>
                <p>Please enable JavaScript to use file uploader.</p>
            </noscript>
        </div>""").render(Context({}))
        return mark_safe(html)


class AttachmentsWidget(forms.TextInput):
    class Media:
        js = (
            "%sjs/fileuploader.js" % STATIC_PREFIX,
            "%sjs/create_event/attachments.js" % STATIC_PREFIX,
        )

        css = {'all': (
            "%sajaxuploader/css/fileuploader.css" % STATIC_PREFIX,
        )}

    def __init__(self, *args, **kwargs):
        super(AttachmentsWidget, self).__init__(*args, **kwargs)
        self.attachments = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):
        if value == "/media/":
            value = ""
        if value:
            html = self.attachments.render("attachments", "", {"id": 'id_attachments', "value": "%s" % (value)})
        else:
            html = self.attachments.render("attachments", "", {"id": 'id_attachments'})

        html += Template("""<div id="attachments-uploader" data-csrf-token="{{ csrf_token }}">
            <noscript>
                <p>Please enable JavaScript to use file uploader.</p>
            </noscript>
        </div>""").render(Context({}))
        return mark_safe(html)


class EventImagesWidget(forms.TextInput):
    class Media:
        js = (
            "%simage_cropping/js/jquery.Jcrop.min.js" % STATIC_PREFIX,
            "%sjs/fileuploader.js" % STATIC_PREFIX,
            "%sjs/create_event/images.js" % STATIC_PREFIX,
        )
        css = {'all': (
            "%sajaxuploader/css/fileuploader.css" % STATIC_PREFIX,
        )}

    def __init__(self, *args, **kwargs):
        super(EventImagesWidget, self).__init__(*args, **kwargs)
        self.images = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):
        if value:
            html = self.images.render("images", "", {"id": 'id_images', "value": "%s" % (value)})
        else:
            html = self.images.render("images", "", {"id": 'id_images'})

        html += Template("""<div id="images-uploader" data-csrf-token="{{ csrf_token }}">
            <noscript>
                <p>Please enable JavaScript to use file uploader.</p>
            </noscript>
        </div>""").render(Context({}))
        return mark_safe(html)


class ChooseUserContextWidget(forms.Widget):
    class Media:
        js = (
            "js/create_event/venue_account_owner.js",
        )

    def __init__(self, account, *args, **kw):
        created_by_admin = kw.pop('by_admin', False)
        super(ChooseUserContextWidget, self).__init__(*args, **kw)
        self.account = account

        self.choices = [{
            "id": account.id,
            "type": "account",
            "text": account.user.username,
            "fullname": ""
        }]

        if created_by_admin:
            # if an event is created by admin, then get all venue accounts
            venue_accounts = VenueAccount.objects.order_by('venue__name').all()
        else:
            # else get venue accounts, that belong to the given account
            venue_accounts = account.venueaccount_set.all()

        for venue_account in venue_accounts:
            self.choices.append({
                "id": venue_account.id,
                "type": "venue_account",
                "text": venue_account.venue.name,
                "fullname": unicode(venue_account.venue)
            })

        self.user_context_type = forms.widgets.HiddenInput()
        self.user_context_id = forms.widgets.HiddenInput()


    def value_from_datadict(self, data, files, name):
        user_context_type = self.user_context_type.value_from_datadict(data, files, 'user_context_type')
        user_context_id = int(self.user_context_id.value_from_datadict(data, files, 'user_context_id'))
        
        if user_context_type=="account":
            return None
        else:
            return user_context_id

    def render(self, name, value, *args, **kwargs):
        html = """
            <div class="dropdown venue-account-owner-dropdown" data-dropdown-class="venue-account-owner-dropdown-list">
                <select id="id_venue_account_owner">
        """
        for choice in self.choices:
            html += "<option"
            if choice["id"] == value:
                html += " selected='selected'"
            html += " value=\"%s|%d|%s\">%s</option>" % (choice["type"], choice["id"], choice["fullname"], choice["text"])

        html += """</select></div>"""

        if value:
            user_context_type = "venue_account"
            user_context_id = value
        else:
            user_context_type = "account"
            user_context_id = self.account.id


        html += self.user_context_type.render("user_context_type", "", {"id": 'id_user_context_type', "value": user_context_type})
        html += self.user_context_id.render("user_context_id", "", {"id": 'id_user_context_id', "value": user_context_id})

        return mark_safe(html)
