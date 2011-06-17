import random
import string
from event.models import Event
from django import forms

def create_key():
    """
    Return a random fourty character alphanumeric string
    Statistically unlikely to collide with an existing string
    """
    return ''.join(random.choice(string.ascii_letters + '0123456789') for x in xrange(40) )

def get_event(auth_key):
    """
    Returns the event which matches the auth_key
    Throws ObjectDoesNotExist if not found
    """
    return Event.events.get(authentication_key__exact=auth_key)

def generate_form(*args):
    """
    Generates an event form
    """
    class _EventForm(forms.ModelForm):
        class Meta:
            model = Event
            exclude = tuple(args)
    return _EventForm
