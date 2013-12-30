import datetime

from django.core.urlresolvers import reverse

from accounts.models import VenueAccount
from event.models import Event
from notices import services as notice_services


def unlink_venue_account(venue_account, after_action, owner, user):
    """ Unlink venue account and move events to another owner.

    @type venue_account: accounts.models.VenueAccount
    @type after_action: unicode
    @param after_action: action to perform after unlinking
    @type owner: unicode
    @param owner: owner, to which have to transfer events, with structure "owner_type"_"owner_id"
    @type user: django.contrib.auth.models.User
    @param user: user, who owns the account
    """
    if after_action == 'move_events':
        _transfer_venue_events_to_owner(venue_account, owner, user)
    elif after_action == 'remove_events':
        _delete_venue_events(venue_account, user)

    venue_account.delete()


def _transfer_venue_events_to_owner(venue_account, owner, user):
    """ Transfer events to another owner (venue account).

    @type venue_account: accounts.models.VenueAccount
    @type owner: unicode
    @type user: django.contrib.auth.models.User
    """
    owner_data = owner.split('_')
    owner_name, owner_link = '', ''
    venue_events = Event.events.filter(venue_account_owner=venue_account)
    if owner_data[0] == 'user':
        owner_name = user.username
        owner_link = reverse('userena_profile_detail', kwargs={'username': user.username})
        for event in venue_events:
            event.venue_account_owner = None
            event.save(update_fields=['venue_account_owner'])
    elif owner_data[0] == 'venue':
        venue_account_owner = VenueAccount.objects.get(id=owner_data[1])
        if venue_account_owner and venue_account_owner.account.user == user:
            owner_name = venue_account_owner.venue.name
            owner_link = reverse('public_venue_account', kwargs={'slug': venue_account_owner.slug})
            for event in venue_events:
                event.venue_account_owner = venue_account_owner
                event.save(update_fields=['venue_account_owner'])

    notice_services.create_notice(notice_type='venue_unlinking_and_events_transferring',
                                  user=user,
                                  notice_data={
                                      'unlinked_venue_name': venue_account.venue.name,
                                      'unlinked_venue_link': reverse('public_venue_account',
                                                                     kwargs={'slug': venue_account.slug}),
                                      'owner_name': owner_name,
                                      'owner_link': owner_link,
                                      'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p')
                                  })


def _delete_venue_events(venue_account, user):
    """ Delete all venue events.

    @type venue_account: accounts.models.VenueAccount
    @type user: django.contrib.auth.models.User
    """
    venue_events = Event.events.filter(venue_account_owner=venue_account)
    for event in venue_events:
        event.delete()

    notice_services.create_notice(notice_type='venue_unlinking_and_events_deleting',
                                  user=user,
                                  notice_data={
                                      'unlinked_venue_name': venue_account.venue.name,
                                      'unlinked_venue_link': reverse('public_venue_account',
                                                                     kwargs={'slug': venue_account.slug}),
                                      'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p')
                                  })