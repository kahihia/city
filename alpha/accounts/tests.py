"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from django.contrib.auth.models import User
from accounts.models import Account, InTheLoopSchedule
from cities.models import Region, City, Country
from event.models import Venue, Event


class InTheLoopSettingsTests(TestCase):
    def test_account_should_be_informed_about_tag_in_region_he_interested_in(self):
        """
        User should be informed about event that appeared in region that he is interested in
        """

        user = User.objects.create_user(username='test', email="jaromudr@gmail.com",  password="pass")
        account = Account(
            user=user,
            all_of_canada=False,
            regions=[Region.objects.filter(name="Alberta"), Region.objects.filter(name="Saskatchewan")]
            tags=["boo"]
        )

        venue = Venue(
            name="Test venue",
            city=City.objects.filter(name="Saskatoon"),
            country=Country.objects.filter(name="Canada")
        )

        event = Event(
            name="Test event",
            venue=venue,
            tags=["boo"]
        )

        self.assertIn(
            event,
            InTheLoopSchedule.unprocessed_for_account(account)
        )        
