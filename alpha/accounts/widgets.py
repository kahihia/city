import copy

from django.utils import simplejson as json
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from taggit_autosuggest.utils import edit_string_for_tags
from cities.models import City


MAX_SUGGESTIONS = getattr(settings, 'TAGGIT_AUTOSUGGEST_MAX_SUGGESTIONS', 20)


class InTheLoopTagAutoSuggest(forms.TextInput):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, basestring):
            tags = [o.tag for o in value.select_related("tag")]
            value = edit_string_for_tags(tags)

        result_attrs = copy.copy(attrs)
        result_attrs['type'] = 'hidden'
        result_html = super(InTheLoopTagAutoSuggest, self).render(name, value, result_attrs)

        widget_attrs = copy.copy(attrs)
        widget_attrs['id'] += '__tagautosuggest'
        widget_html = super(InTheLoopTagAutoSuggest, self).render(name, value, widget_attrs)

        js = u"""
            <script type="text/javascript">
            (function ($) {
                var tags_as_string;

                $(document).ready(function (){
                    tags_as_string = $('#%(result_id)s').val();

                    $("#%(widget_id)s").autoSuggest("%(url)s", {
                        asHtmlID: "%(widget_id)s",
                        startText: "%(start_text)s",
                        emptyText: "%(empty_text)s",
                        limitText: "%(limit_text)s",
                        preFill: tags_as_string,
                        queryParam: 'q',
                        retrieveLimit: %(retrieve_limit)d,
                        minChars: 1,
                        neverSubmit: true
                    });

                    $('.as-selections').addClass('vTextField');
                    $('ul.as-selections li.as-original input').addClass('vTextField');

                    $('#%(result_id)s').parents().find('form').submit(function (){
                        tags_as_string = $("#as-values-%(widget_id)s").val();
                        $("#%(widget_id)s").remove();
                        $("#%(result_id)s").val(tags_as_string);
                    });
                });
            })(jQuery || django.jQuery);
            </script>""" % {
                'result_id': result_attrs['id'],
                'widget_id': widget_attrs['id'],
                'url': reverse('in_the_loop_tags'),
                'start_text': _("Enter Tag Here"),
                'empty_text': _("No Results"),
                'limit_text': _('No More Selections Are Allowed'),
                'retrieve_limit': MAX_SUGGESTIONS,
            }
        return result_html + widget_html + mark_safe(js)
    
    class Media:
        css_filename = getattr(settings, 'TAGGIT_AUTOSUGGEST_CSS_FILENAME',
            'autoSuggest.css')
        js_base_url = getattr(settings, 'TAGGIT_AUTOSUGGEST_STATIC_BASE_URL',
            '%sjquery-autosuggest' % settings.STATIC_URL)
        css = {
            'all': ('%s/css/%s' % (js_base_url, css_filename),)
        }
        js = (
            '%s/js/jquery.autoSuggest.minified.js' % js_base_url,
        )


class CityAutoSuggest(forms.TextInput):
    input_type = 'text'

    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, basestring):
            cities = City.objects.filter(id__in=value)
            cities_as_objects = [{
                "name": city.__unicode__(),
                "value": str(city.id)
            } for city in cities]
        else:
            cities_as_objects = {}

        result_attrs = copy.copy(attrs)
        result_attrs['type'] = 'hidden'
        result_html = super(CityAutoSuggest, self).render(name, value, result_attrs)

        widget_attrs = copy.copy(attrs)
        widget_attrs['id'] += '__cityautosuggest'
        widget_html = super(CityAutoSuggest, self).render(name, value, widget_attrs)

        js = u"""
            <script type="text/javascript">
            (function ($) {
                var cities_as_objects = %(cities_as_objects)s;

                $(document).ready(function (){

                    $("#%(widget_id)s").autoSuggest("%(url)s", {
                        asHtmlID: "%(widget_id)s",
                        startText: "%(start_text)s",
                        emptyText: "%(empty_text)s",
                        limitText: "%(limit_text)s",
                        preFill: cities_as_objects,
                        queryParam: 'q',
                        retrieveLimit: %(retrieve_limit)d,
                        minChars: 1,
                        neverSubmit: true,
                        selectedValuesProp: "value",
                        selectedItemProp: "name",
                        searchObjProps: "name",
                        canGenerateNewSelections: false
                    });

                    $('.as-selections').addClass('vTextField');
                    $('ul.as-selections li.as-original input').addClass('vTextField');

                    $('#%(result_id)s').parents().find('form').submit(function (){
                        cities_as_objects = $("#as-values-%(widget_id)s").val();
                        $("#%(widget_id)s").remove();
                        $("#%(result_id)s").val(cities_as_objects);
                    });
                });
            })(jQuery || django.jQuery);
            </script>""" % {
                'result_id': result_attrs['id'],
                'widget_id': widget_attrs['id'],
                'url': reverse('cities_autosuggest'),
                'start_text': _("Add city here"),
                'empty_text': _("No Results"),
                'limit_text': _('No More Selections Are Allowed'),
                'retrieve_limit': MAX_SUGGESTIONS,
                'cities_as_objects': json.dumps(cities_as_objects)
            }
        return result_html + widget_html + mark_safe(js)
    
    class Media:
        css_filename = getattr(settings, 'TAGGIT_AUTOSUGGEST_CSS_FILENAME',
            'autoSuggest.css')
        js_base_url = getattr(settings, 'TAGGIT_AUTOSUGGEST_STATIC_BASE_URL',
            '%sjquery-autosuggest' % settings.STATIC_URL)
        css = {
            'all': ('%s/css/%s' % (js_base_url, css_filename),)
        }
        js = (
            '%s/js/jquery.autoSuggest.minified.js' % js_base_url,
        )


class ChooseUserContextWidget(forms.Widget):
    class Media:
        js = (
            "js/create_event/venue_account_owner.js",
        )

    def __init__(self, account, *args, **kw):        
        super(ChooseUserContextWidget, self).__init__(*args, **kw)
        self.account = account

        self.choices = [{
            "id": account.id,
            "type": "account",
            "text": account.user.username,
            "fullname": ""
        }]

        for venue_account in account.venueaccount_set.all():
            self.choices.append({
                "id": venue_account.id,
                "type": "venue_account",
                "text": venue_account.venue.name,
                "fullname": venue_account.venue
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
        html = """<div class="dropdown venue-account-owner-dropdown" data-dropdown-class="venue-account-owner-dropdown-list"><select id="id_venue_account_owner">"""
        for choice in self.choices:
            html += "<option"
            if choice["id"] == value:
                html += " selected='selected'"
            html += " value='%s|%d|%s'>%s</option>" % (choice["type"], choice["id"], choice["fullname"], choice["text"])

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

