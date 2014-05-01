import datetime
import json

from django.core.urlresolvers import reverse
from django.contrib.gis.geos import Point

from cities.models import Country, City

from accounts.models import Account, VenueAccount
from event.models import Event, Venue
from event.services import event_service
from notices import services as notice_service
from notices.models import Notice
from ..models import VenueAccountTransferring
from . import social_links_services


def unlink_venue_account(venue_account, after_action, owner, user):
    """ Unlink a venue account and move events to another owner.

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


def change_venue_owner(venue_account_id, owner_id):
    """ Change owner of a venue with the given id.

    @type venue_account_id: int
    @type owner_id: int
    @param owner_id: a new owner id
    @rtype: bool
    """
    result = False
    target = Account.objects.get(user_id=owner_id)
    venue_account = VenueAccount.objects.get(id=venue_account_id)
    if target and venue_account:
        venue_account_transferring = VenueAccountTransferring.objects.create(target=target,
                                                                             venue_account=venue_account)
        target_name = target.user.username
        target_link = reverse('userena_profile_detail', kwargs={'username': target.user.username})
        notice_service.create_notice(notice_type='venue_transferring_to_owner',
                                     user=venue_account.account.user,
                                     notice_data={
                                         'venue_name': venue_account.venue.name,
                                         'venue_link': reverse('public_venue_account',
                                                               kwargs={'slug': venue_account.slug}),
                                         'target_name': target_name,
                                         'target_link': target_link,
                                         'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p'),
                                     })

        notice_service.create_notice('venue_transferring', target.user, {
            'subject': 'CityFusion: venue has been transferred to you.',
            'user': target.user,
            'venue_account': venue_account
        }, {
            'venue_name': venue_account.venue.name,
            'venue_link': reverse('public_venue_account', kwargs={'slug': venue_account.slug}),
            'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p'),
            'accept_link': reverse('accept_venue_transferring', kwargs={
                'venue_transferring_id': venue_account_transferring.id}),
            'reject_link': reverse('reject_venue_transferring', kwargs={
                'venue_transferring_id': venue_account_transferring.id})
        })

        result = True
    return result


def change_venues_owner(venue_account_ids, owner_id):
    """ Change owner of venues list.

    @type venue_account_ids: list
    @type owner_id: int
    @param owner_id: a new owner id
    @rtype: int
    """
    transferred_accounts, counter = [], 0
    for venue_account_id in venue_account_ids:
        counter += 1
        try:
            venue_account = VenueAccount.objects.get(pk=venue_account_id)
            target = Account.objects.get(user_id=owner_id)
            if venue_account.account == target:
                raise Exception('The venue is already belongs to this account')

            if VenueAccountTransferring.objects.filter(target=target, venue_account=venue_account).count() > 0:
                raise Exception('The venue is already in the transfer process')

            venue_account_transferring = VenueAccountTransferring.objects.create(target=target,
                                                                                 venue_account=venue_account)
            transferred_accounts.append(venue_account)
            target_name = target.user.username
            target_link = reverse('userena_profile_detail', kwargs={'username': target.user.username})
            notice_service.create_notice(notice_type='venue_transferring_to_owner',
                                         user=venue_account.account.user,
                                         notice_data={
                                             'venue_name': venue_account.venue.name,
                                             'venue_link': reverse('public_venue_account',
                                                                   kwargs={'slug': venue_account.slug}),
                                             'target_name': target_name,
                                             'target_link': target_link,
                                             'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p'),
                                         })

            if counter == len(venue_account_ids):
                mail_data = {'subject': 'CityFusion: venues has been transferred to you.',
                             'user': target.user,
                             'venue_accounts': transferred_accounts
                }
            else:
                mail_data = {}

            notice_service.create_notice('venue_transferring', target.user, mail_data, {
                'venue_name': venue_account.venue.name,
                'venue_link': reverse('public_venue_account', kwargs={'slug': venue_account.slug}),
                'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p'),
                'accept_link': reverse('accept_venue_transferring', kwargs={
                    'venue_transferring_id': venue_account_transferring.id}),
                'reject_link': reverse('reject_venue_transferring', kwargs={
                    'venue_transferring_id': venue_account_transferring.id})
            }, mail_template='mail/venues_transferring.txt')
        except Exception as e:
            raise Exception(e.message)
    return len(transferred_accounts)


def accept_venue_transferring(venue_transferring_id, notice_id):
    """ Accept a venue transferring.

    @type venue_transferring_id: int
    @type notice_id: int
    @rtype: bool
    """
    result = False
    try:
        venue_transferring = VenueAccountTransferring.objects.get(pk=venue_transferring_id)
    except VenueAccountTransferring.DoesNotExist:
        venue_transferring = None

    if venue_transferring and venue_transferring.target:
        venue_account = venue_transferring.venue_account
        from_user = venue_transferring.venue_account.account.user
        target = venue_transferring.target.user

        venue_account.account = venue_transferring.target
        venue_account.save()

        venue_account.venue.user = venue_transferring.target.user
        venue_account.venue.save()

        Event.events.filter(venue_account_owner_id=venue_account.id).update(owner=venue_transferring.target.user.id)

        venue_transferring.delete()
        try:
            notice = Notice.objects.get(pk=notice_id)
        except Notice.DoesNotExist:
            notice = None

        if notice:
            notice_data = json.loads(notice.log)
            notice_data['state'] = 'Accepted'
            notice.log = json.dumps(notice_data)
            notice.read = True
            notice.save()

            target_name = target.username
            target_link = reverse('userena_profile_detail', kwargs={'username': target.username})
            notice_service.create_notice('venue_transferring_accepting', from_user, {
                'subject': 'Cityfusion: transferring of your venue has been accepted.',
                'user': from_user,
                'venue_account': venue_account,
                'target_name': target_name,
                'target_link': target_link,
            }, {
                'venue_name': venue_account.venue.name,
                'venue_link': reverse('public_venue_account', kwargs={'slug': venue_account.slug}),
                'target_name': target_name,
                'target_link': target_link,
                'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p'),
            })

        result = True
    return result


def reject_venue_transferring(venue_transferring_id, notice_id):
    """ Reject a venue transferring.

    @type venue_transferring_id: int
    @type notice_id: int
    @rtype: bool
    """
    result = False
    try:
        venue_transferring = VenueAccountTransferring.objects.get(pk=venue_transferring_id)
    except VenueAccountTransferring.DoesNotExist:
        venue_transferring = None

    if venue_transferring and venue_transferring.target:
        venue_account = venue_transferring.venue_account
        from_user = venue_transferring.venue_account.account.user
        target = venue_transferring.target.user

        venue_transferring.delete()
        try:
            notice = Notice.objects.get(pk=notice_id)
        except Notice.DoesNotExist:
            notice = None

        if notice:
            notice_data = json.loads(notice.log)
            notice_data['state'] = 'Rejected'
            notice.log = json.dumps(notice_data)
            notice.read = True
            notice.save()

            target_name = target.username
            target_link = reverse('userena_profile_detail', kwargs={'username': target.username})
            notice_service.create_notice('venue_transferring_rejecting', from_user, {
                'subject': 'Cityfusion: transferring of your venue has been rejected.',
                'user': from_user,
                'venue_account': venue_account,
                'target_name': target_name,
                'target_link': target_link,
            }, {
                'venue_name': venue_account.venue.name,
                'venue_link': reverse('public_venue_account', kwargs={'slug': venue_account.slug}),
                'target_name': target_name,
                'target_link': target_link,
                'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p'),
            })

        result = True
    return result


def save_venue(data, form):
    """ Save an instance of Venue class.
    """
    venue = form.save()

    venue.city = City.objects.get(id=int(data.get('city_identifier')))
    venue.country = Country.objects.get(name='Canada')
    venue.location = Point((
        float(data.get('location_lng')),
        float(data.get('location_lat'))
    ))
    venue.save()


def delete_venue(venue):
    """ Delete an instance of Venue class.
    """
    venue_accounts = VenueAccount.objects.filter(venue=venue)
    for venue_account in venue_accounts:
        venue_account.delete()

    venue_events = Event.events.filter(venue=venue)
    for event in venue_events:
        event.delete()

    venue.delete()


def prepare_venue_account_edit_initial_data(venue_account):
    return {
        'picture_src': '/media/%s' % venue_account.picture,
        'social_links': social_links_services.prepare_social_links(venue_account),
        'venue_identifier': event_service.prepare_initial_venue_id(venue_account),
        'place': event_service.prepare_initial_place(venue_account),
        'location': event_service.prepare_initial_location(venue_account),
        'linking_venue_mode': 'EXIST'
    }


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

    notice_service.create_notice(notice_type='venue_unlinking_and_events_transferring',
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

    notice_service.create_notice(notice_type='venue_unlinking_and_events_deleting',
                                  user=user,
                                  notice_data={
                                      'unlinked_venue_name': venue_account.venue.name,
                                      'unlinked_venue_link': reverse('public_venue_account',
                                                                     kwargs={'slug': venue_account.slug}),
                                      'date': datetime.datetime.now().strftime('%A, %b. %d, %I:%M %p')
                                  })