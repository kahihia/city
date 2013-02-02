"""Custom Map widget."""
from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.gis.geos import Point

DEFAULT_WIDTH = 400
DEFAULT_HEIGHT = 400

DEFAULT_LNG = -79.4163
DEFAULT_LAT = 43.70011


JSMIN = getattr(settings, 'GMAPI_JSMIN', not settings.DEBUG) and '.min' or ''

JQUERY_URL = getattr(settings, 'GMAPI_JQUERY_URL',
                     'http://ajax.googleapis.com/ajax/libs/jquery/1.4/'
                     'jquery%s.js' % JSMIN)

MAPS_URL = getattr(settings, 'GMAPI_MAPS_URL',
                   'http://maps.google.com/maps/api/js?sensor=false')

# Same rules apply as ADMIN_MEDIA_PREFIX.
# Omit leading slash to make relative to MEDIA_URL.
MEDIA_PREFIX = getattr(settings, 'GMAPI_MEDIA_PREFIX', 'gmapi/')


class LocationWidget(forms.TextInput):
    def __init__(self, *args, **kw):
        self.map_width = kw.get("map_width", DEFAULT_WIDTH)
        self.map_height = kw.get("map_height", DEFAULT_HEIGHT)

        super(LocationWidget, self).__init__(*args, **kw)
        self.lng_widget = forms.widgets.HiddenInput()
        self.lat_widget = forms.widgets.HiddenInput()

    def value_from_datadict(self, data, files, name):
        return Point((
            float(self.lng_widget.value_from_datadict(data, files, name + '_lng')),
            float(self.lat_widget.value_from_datadict(data, files, name + '_lat'))
        ))

    def render(self, name, value, *args, **kwargs):
        if value is None:
            lat, lng = DEFAULT_LAT, DEFAULT_LNG
        else:
            if isinstance(value, unicode):
                a, b = value.split(',')
            else:
                a, b = value
            lat, lng = float(a), float(b)

        js = '''
<script type="text/javascript">
//<![CDATA[
    var map_%(name)s,
        marker_%(name)s,
        infowindow;

    function savePosition_%(name)s(point)
    {
        var lng = document.getElementById("id_%(name)s_lng"),
            lat = document.getElementById("id_%(name)s_lat");
        lng.value = point.lng().toFixed(6);
        lat.value = point.lat().toFixed(6);
        map_%(name)s.panTo(point);
    }

    function load_%(name)s() {
        var point = new google.maps.LatLng(%(lat)f, %(lng)f);

        infowindow = new google.maps.InfoWindow({
            content: "<div class='map-held'>Hi, I'm your Event's location!<br>Please move me along the map<br>to the exact location your<br>event is being held.</div>"
        });

        var options = {
            zoom: 14,
            center: point,
            mapTypeId: google.maps.MapTypeId.ROADMAP
            // mapTypeControl: true,
            // navigationControl: true
        };

        map_%(name)s = new google.maps.Map(document.getElementById("map_%(name)s"), options);

        var marker = new google.maps.Marker({
                map: map_%(name)s,
                position: new google.maps.LatLng(%(lat)f, %(lng)f),
                draggable: true

        });

        marker_%(name)s = marker;
        google.maps.event.addListener(marker, 'dragend', function(mouseEvent) {
            savePosition_%(name)s(mouseEvent.latLng);
        });

        google.maps.event.addListener(map_%(name)s, 'click', function(mouseEvent){
            marker.setPosition(mouseEvent.latLng);
            savePosition_%(name)s(mouseEvent.latLng);
        });

    }

    jQuery(document).ready(function(){
        setTimeout(function(){
            load_%(name)s();
        });
    });

//]]>
</script>
        ''' % dict(name=name, lat=lat, lng=lng)
        html = self.lng_widget.render("%s_lng" % name, lng, dict(id='id_%s_lng' % name))
        html += self.lat_widget.render("%s_lat" % name, lat, dict(id='id_%s_lat' % name))
        html += '<div id="map_%s" style="width: %dpx; height: %dpx"></div>' % (name, self.map_width, self.map_height)

        return mark_safe(js + html)

    #class Media:
    #    js = (
    #        'http://maps.google.com/maps/api/js?sensor=false',
    #    )
