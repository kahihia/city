from django import forms
from .models import Feedback

class ContactForm(forms.ModelForm):
    class Meta:
        model = Feedback
    def __init__(self,*args,**kwargs):
        kwargs['label_suffix'] = ''
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'text wide'
        self.fields['email'].widget.attrs['class'] = 'text wide'
        self.fields['comments'].widget = forms.widgets.Textarea( attrs={ 'class':'wide', 'rows':6 } )
    def as_p(self):
        return self._html_output(
            normal_row = u'<p%(html_class_attr)s>%(label)s %(field)s%(help_text)s%(errors)s</p>',
            error_row = u'%s',
            row_ender = '</p>',
            help_text_html = u' %s',
            errors_on_separate_row = False)
    
