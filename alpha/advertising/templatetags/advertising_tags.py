from django import template
from django.template.base import Node, NodeList, TemplateSyntaxError
from ..models import Advertising
register = template.Library()


class RandomNode(Node):
    def __init__(self, nodelist_options):
        self.nodelist_options = nodelist_options

    def render(self, context):
        from random import choice
        return choice(self.nodelist_options).render(context)


def do_random(parser, token):
    """
    Output the contents of a random block.

    The `random` block tag must contain one or more `or` tags, which separate
    possible choices; a choice in this context is everything between a
    `random` and `or` tag, between two `or` tags, or between an `or` and an
    `endrandom` tag.

    Sample usage::

        {% random %}
            You will see me half the time.
        {% or %}
            You will see <em>me</em> the other half.
        {% endrandom %}
    """
    options = NodeList()

    while True:
        option = parser.parse(('or', 'endrandom'))
        token = parser.next_token()
        options.append(option)
        if token.contents == 'or':
            continue
        parser.delete_first_token()
        break
    if len(options) < 2:
        raise TemplateSyntaxError
    return RandomNode(options)

register.tag('random', do_random)


@register.inclusion_tag('advertising/advertising.html', takes_context=True)
def advertising(context, dimensions):
    # request = context['request']

    width, height = map(lambda x: int(x), dimensions.split("x"))

    try:
        advertising = Advertising.objects.filter(ad_type__width=width, ad_type__height=height).order_by('?')[0]
        advertising.view()
    except:
        advertising = None

    return {
        'advertising': advertising
    }
