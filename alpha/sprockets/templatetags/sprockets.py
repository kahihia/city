from django import template
from django.conf import settings

register = template.Library()

@register.tag
def combine_css(parser, token):
    """
    {% combine css index %}
        {% css event.css %}
        {% css venue.css %}
    {% endcombine %}

    """
    try:
        tag_name, exp, prefix = token.split_contents()
    except ValueError:
        msg = '%r tag requires a prefix for result css filename' % token.contents[0]
        raise template.TemplateSyntaxError(msg)

    nodelist = parser.parse(("endcombine", ))
    parser.delete_first_token()
    if settings.DEBUG:
        return DevCombineNode(nodelist)
    else:
        return ProdCombineNode(nodelist)


class DevCombineNode(template.Node):
    """
    <link href="index-hexcode.css" rel="stylesheet" type="text/css" />
    """
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return self.nodelist.render(context)

class ProdCombineNode(template.Node):
    """
    <link href="{{STATIC_URL}}styles/browse/event_details.css" rel="stylesheet" type="text/css" />

    """
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        pass



class CssNode(template.Node):
    def __init__(self, filename):
        self.filename = filename

    def render(self, context):
        return """<link href="{{STATIC_URL}}%s" rel="stylesheet" type="text/css" />""" % (self.filename)


class JsNode(template.Node):
    def __init__(self, filename):
        self.filename = filename

    def render(self, context):
        return """<script src="{{STATIC_URL}}%s" type="text/javascript"></script>""" % (self.filename)
