from django import forms
from django.utils.safestring import mark_safe

from .models import Feedback


class ChooseSubjectWidget(forms.Widget):

    def __init__(self, *args, **kw):
        super(ChooseSubjectWidget, self).__init__(*args, **kw)

        self.choices = Feedback.TYPE_CHOICES

    def render(self, name, value, *args, **kwargs):
        html = """
            <div class="dropdown type-dropdown" data-dropdown-class="type-dropdown-list">
                <select name="%s" id="id_type">
        """ % name
        for key, value in self.choices:
            html += '<option value="%s">%s</option>' % (key, value)

        html += """</select></div>"""

        return mark_safe(html)