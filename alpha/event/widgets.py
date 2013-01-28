from django import forms
from django.conf import settings
from django.template import Template, Context
from django.forms.widgets import Select, MultiWidget, DateInput, TextInput, RadioSelect
from django.utils.safestring import mark_safe
from time import strftime
from image_cropping.widgets import ImageCropWidget
import json

STATIC_PREFIX = settings.STATIC_URL


class WhenWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        super(WhenWidget, self).__init__(*args, **kwargs)
        #self.when_json = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):
        html = super(WhenWidget, self).render(name, value, *args, **kwargs)
        #html += self.when_json.render("when_json", "", {"id":'id_when_json'})
        return mark_safe(html)

    class Media(object):
        css = {
            'all': (
                u'%scss/datepicker.css' % STATIC_PREFIX,
                u'%scss/when.css' % STATIC_PREFIX,
            )
        }
        js = (
            u'%sjs/jquery-ui.multidatespicker.js' % STATIC_PREFIX,
            u'%sjs/jquery.ui.timepicker.js' % STATIC_PREFIX,
            u'%sjs/jquery.mtz.monthpicker.js' % STATIC_PREFIX,
            u'%sjs/when.js' % STATIC_PREFIX,
        )


class PriceWidget(forms.TextInput):
    class Media(object):
        js = (
            u'%sjs/price.js' % STATIC_PREFIX,
        )

    def render(self, name, value, *args, **kwargs):
        html = """<label for="id_price_free"><input type='checkbox' id="id_price_free">Free</label>"""
        html += super(forms.TextInput, self).render(name, value, *args, **kwargs)
        return mark_safe(html)


class GeoCompleteWidget(forms.TextInput):
    class Media(object):
        js = (
            u'%sjs/jquery.geocomplete.js' % STATIC_PREFIX,
            u'%sjs/init.jquery.geocomplete.js' % STATIC_PREFIX,
        )

    def __init__(self, *args, **kw):
        super(GeoCompleteWidget, self).__init__(*args, **kw)
        self.geo_venue = forms.widgets.HiddenInput()
        self.geo_street = forms.widgets.HiddenInput()
        self.geo_city = forms.widgets.HiddenInput()
        self.geo_country = forms.widgets.HiddenInput()
        self.geo_longtitude = forms.widgets.HiddenInput()
        self.geo_latitude = forms.widgets.HiddenInput()

    def render(self, name, value, *args, **kwargs):
        html = super(GeoCompleteWidget, self).render(name, value, *args, **kwargs)
        html += "<div class='geo-details'>"
        html += self.geo_venue.render("geo_venue", "", {"id": 'id_geo_venue', 'data-geo': "name"})
        html += self.geo_street.render("geo_street", "", {"id": 'id_geo_street', 'data-geo': "route"})
        html += self.geo_city.render("geo_city", "", {"id": 'id_geo_city', 'data-geo': "locality"})
        html += self.geo_country.render("geo_country", "", {"id": 'id_geo_country', 'data-geo': "country"})
        html += self.geo_longtitude.render("geo_longtitude", "", {"id": 'id_geo_longtitude', 'data-geo': "lng"})
        html += self.geo_latitude.render("geo_latitude", "", {"id": 'id_geo_latitude', 'data-geo': "lat"})
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


class WheelchairWidget(RadioSelect):
    class Media(object):
        js = (
            u'%sjs/wheelchair.js' % STATIC_PREFIX,
        )


class DescriptionWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super(DescriptionWidget, self).__init__(*args, **kwargs)
        self.description_json = forms.widgets.HiddenInput()

    #def render(self, name, value, *args, **kwargs):
    #    html = super(DescriptionWidget, self).render(name, value, *args, **kwargs)
    #    html += self.description_json.render("description_json", "", {"id":'id_description_json'})
    #    return mark_safe(html)

    class Media(object):
        js = (
            u'%sjs/description.js' % STATIC_PREFIX,
        )


class JqSplitDateTimeWidget(MultiWidget):

    def __init__(self, attrs=None, date_format=None, time_format=None):
        date_class = attrs['date_class']
        time_class = attrs['time_class']
        del attrs['date_class']
        del attrs['time_class']

        time_attrs = attrs.copy()
        time_attrs['class'] = time_class
        date_attrs = attrs.copy()
        date_attrs['class'] = date_class

        widgets = (DateInput(attrs=date_attrs, format=date_format),
                   TextInput(attrs=time_attrs), TextInput(attrs=time_attrs),
                   Select(attrs=attrs, choices=[('AM', 'AM'), ('PM', 'PM')]))

        super(JqSplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            d = strftime('%Y-%m-%d', value.timetuple())
            hour = strftime('%I', value.timetuple())
            minute = strftime('%M', value.timetuple())
            meridian = strftime('%p', value.timetuple())
            return (d, hour, minute, meridian)
        else:
            return (None, None, None, None)

    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), it inserts an HTML
        linebreak between them.

        Returns a Unicode string representing the HTML for the whole lot.
        """
        return 'Date: %s<br/>Time: %s:%s %s' % (rendered_widgets[0], rendered_widgets[1],
                                                rendered_widgets[2], rendered_widgets[3])

    class Media:
        css = (
            'css/overcast/jquery-ui-1.8.13.custom.css'
            )
        js = (
            'js/mylibs/jquery-1.5.1.min.js',
            'js/mylibs/jquery-ui-1.8.13.custom.min.js',
            'js/jqsplitdatetime.js'
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
