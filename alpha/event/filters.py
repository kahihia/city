from models import Event, Venue, SingleEvent
import datetime
import dateutil.parser as dateparser
from accounts.models import VenueType
from django.db.models import Q, Count
from cities.models import Region, City
import urllib


class Filter(object):
    def __init__(self, name, field, lookup=None):
        self.field = field
        self.lookup = lookup
        self.name = name

    def filter(self, qs, value):
        if not value:
            return qs

        if not self.lookup:
            lookup = "exact"
        else:
            lookup = self.lookup

        return qs.filter(**{'%s__%s' % (self.field, lookup): value})

    def url_query(self, querydict):
        return "%s=%s" % (self.name, querydict[self.name])

    def upgrade_value(self, querydict, value):
        return value

    def filter_data(self, querydict, default=None):
        if self.name in querydict:
            return querydict[self.name]
        return default

    def search_tags(self, value):
        return None


class DateFilter(Filter):
    def filter(self, qs, value):
        if not value:
            return qs

        if not self.lookup:
            lookup = "exact"
        else:
            lookup = self.lookup

        return qs.filter(**{'%s__%s' % (self.field, lookup): value})


class TimeFilter(Filter):
    def filter(self, qs, value):
        if self.lookup == "gte":
            operation = ">="
        else:
            operation = "<="

        where = 'EXTRACT(hour from %s) %s %s' % (self.field, operation, value)

        return qs.extra(where=[where])


class TagsFilter(Filter):
    def filter(self, qs, tags):
        # TODO: It is code with bad performance
        event_ids = map(lambda event: event.event.id, qs)
        event_ids_with_tags = Event.events.filter(id__in=list(event_ids)).filter( 
            tagged_items__tag__name__in=tags 
        ).annotate(
            repeat_count=Count('id') 
        ).filter( 
            repeat_count=len(tags) 
        ).values_list("id", flat=True)
        return qs.filter(event_id__in=list(event_ids_with_tags))

    def url_query(self, querydict):
        tags = querydict["tag"]
        if isinstance(tags, basestring):
            tags = querydict.getlist(self.name)
        return "&".join(["tag=%s" % urllib.quote(tag.encode('utf8')) for tag in tags])

    def upgrade_value(self, querydict, value):
        return_value = []
        if self.name in querydict:
            return_value = querydict.getlist(self.name)
            if value in return_value:
                return_value.remove(value)
            else:
                return_value.append(value)
        else:
            return_value = [value]
        return return_value

    def filter_data(self, querydict, default=[]):
        if self.name in querydict:
            return querydict.getlist(self.name)
        return default

    def search_tags(self, tags):
        tags_to_return = []
        for tag in tags:
            tags_to_return.append({
                "name": tag,
                "remove_url": "?" + self.parent.url_query(tag=tag)
            })
        return tags_to_return


search_tags_for_filters = {
    "recently_featured": "Recently featured",
    "random": "Random",
    "top_viewed": "Top viewed",
    "latest": "Recently added",
    "night_life": "Night life",
    "date_night": "Date night",
    "free": "Free",
    "family": "Family",
    "reminder": "Reminder",
    "in_the_loop": "In the Loop"
}


class FunctionFilter(Filter):
    def __init__(self, name, account=None):
        self.name = name
        self.account = account

    def filter(self, qs, value):
        return getattr(self, "%s_filter" % value)(qs)

    def random_filter(self, qs):
        return qs.order_by("?")

    def tags_filter(self, qs):
        return qs

    def recently_featured_filter(self, qs):
        return qs.filter(event__featuredevent__isnull=False)\
                 .order_by('event__featuredevent__start_time', 'event', 'start_time')\
                 .distinct('event__featuredevent__start_time', 'event')

    # def reminder_filter(self, qs):
    #     ids = self.account.reminder_events.all().values_list("id", flat=True)
    #     return qs.filter(event_id__in=ids) ---- _rem_

    def in_the_loop_filter(self, qs):
        ids = self.account.in_the_loop_events().values_list("event_id", flat=True)
        return qs.filter(event_id__in=ids)

    def all_filter(self, qs):
        return qs

    def top_viewed_filter(self, qs):
        return qs.order_by("event__viewed_times")

    def latest_filter(self, qs):
        return qs.order_by("-event__created")

    def night_life_filter(self, qs):
        ids = qs.filter(
            Q(event__tagged_items__tag__name__in=["19+", "Night Life", "DJ", "Party", "Rave"]) | Q(event__venue__venueaccount__types=VenueType.active_types.get(name='Nightlife & Singles & Night Clubs'))
        ).values_list("event_id", flat=True)
        return qs.filter(event_id__in=ids)

    def date_night_filter(self, qs):
        return qs.filter(event__tagged_items__tag__name__in=["Date Night"])

    def free_filter(self, qs):
        # TODO: refactor
        single_event_with_tag = SingleEvent.future_events.filter(event__tagged_items__tag__name__in=["Free"])

        single_event_ids = SingleEvent.future_events.extra(
            where=["""
                (setweight(to_tsvector('pg_catalog.english', coalesce("event_singleevent"."description", '')), 'D')) @@ plainto_tsquery('pg_catalog.english', 'free')
            """]
        ).values_list("id", flat=True)

        event_ids = Event.events.extra(
            where=["""                
                (setweight(to_tsvector('pg_catalog.english', coalesce("event_event"."name", "event_event"."description")), 'D')) @@ plainto_tsquery('pg_catalog.english', 'free')
            """]
        ).values_list("id", flat=True)

        return qs.filter(Q(id__in=single_event_with_tag) | Q(id__in=list(single_event_ids)) | Q(event_id__in=list(event_ids)))

    def family_filter(self, qs):
        # https://code.djangoproject.com/ticket/13363
        # TODO: refactor
        single_event_with_tag = SingleEvent.future_events.filter(event__tagged_items__tag__name__in=["Family"])
        single_event_ids = SingleEvent.future_events.extra(
            where=["""
                (setweight(to_tsvector('pg_catalog.english', coalesce("event_singleevent"."description", '')), 'D')) @@ plainto_tsquery('pg_catalog.english', 'family')
            """]
        ).values_list("id", flat=True)

        event_ids = Event.events.extra(
            where=["""                
                (setweight(to_tsvector('pg_catalog.english', coalesce("event_event"."name", "event_event"."description")), 'D')) @@ plainto_tsquery('pg_catalog.english', 'family')
            """]
        ).values_list("id", flat=True)

        return qs.filter(Q(id__in=single_event_with_tag) | Q(id__in=list(single_event_ids)) | Q(event_id__in=list(event_ids)))

    def search_tags(self, function):
        name = search_tags_for_filters.get(function)

        if name:
            return [{
                "name": name,
                "remove_url": "?" + self.parent.url_query(exclude="function")
            }]
        else:
            return None


search_tags_for_periods = {
    "today": "Today",
    "tomorrow": "Tomorrow",
    "this-weekend": "This weekend",
    "next-week": "Next week"
}


class PeriodFilter(Filter):
    def __init__(self, name, start_filter, end_filter):
        self.name = name
        self.start_filter = start_filter
        self.end_filter = end_filter

    def filter(self, qs, value):
        return getattr(self, "%s_filter" % value.replace("-", "_"))(qs)

    def today_filter(self, qs):
        today = datetime.datetime(*(datetime.date.today().timetuple()[:6]))
        start = today
        end = today.replace(hour=23, minute=59, second=59)

        return self.period_filter(qs, start, end)

    def tomorrow_filter(self, qs):
        today = datetime.datetime(*(datetime.date.today().timetuple()[:6]))
        tomorrow = today + datetime.timedelta(days=1)
        start = tomorrow
        end = tomorrow.replace(hour=23, minute=59, second=59)

        return self.period_filter(qs, start, end)

    def this_weekend_filter(self, qs):
        today = datetime.datetime(*(datetime.date.today().timetuple()[:6]))
        end = today + datetime.timedelta(days=6 - today.weekday())
        end = end.replace(hour=23, minute=59, second=59, microsecond=0)
        #sat is 5
        if today.weekday() == 5:
            start = today + datetime.timedelta(days=5 - today.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        #friday at 5pm is the weekend.
        else:
            start = today + datetime.timedelta(days=4 - today.weekday())
            start = start.replace(hour=17, minute=0, second=0, microsecond=0)

        return self.period_filter(qs, start, end)

    def next_week_filter(self, qs):
        today = datetime.datetime(*(datetime.date.today().timetuple()[:6]))
        end = today + datetime.timedelta(days=13 - today.weekday())
        start = today + datetime.timedelta(days=7 - today.weekday())

        return self.period_filter(qs, start, end)

    def period_filter(self, qs, start, end):
        qs = self.start_filter.filter(qs, start)
        qs = self.end_filter.filter(qs, end)
        return qs

    def search_tags(self, period):
        name = search_tags_for_periods.get(period)
        if name:
            return [{
                "name": name,
                "remove_url": "?" + self.parent.url_query(exclude="period")
            }]
        else:
            return None


exclude_shortcuts = {
    "datetime": ["start_date", "end_date", "start_time", "end_time", "period"]
}


class VenueFilter(Filter):
    def search_tags(self, id):
        if id:
            venue = Venue.objects.get(id=id)
            return [{
                "name": venue.name,
                "remove_url": "?" + self.parent.url_query(exclude="venue")
            }]
        else:
            return None


class LocationFilter(Filter):
    def __init__(self, name):
        self.name = name

    def search_tags(self, location):
        return []
        location_type, location_id = location.split("|")
        location_id = int(location_id)

        if location_type == "country":
            return [{
                "name": "Canada",
                "remove_url": "?" + self.parent.url_query(exclude="location")
            }]

        if location_type == "region":
            region = Region.objects.get(id=location_id)
            return [{
                "name": region.name,
                "remove_url": "?" + self.parent.url_query(exclude="location")
            }]

        if location_type == "city":
            city = City.objects.get(id=location_id)
            return [{
                "name": city.name,
                "remove_url": "?" + self.parent.url_query(exclude="location")
            }]

    def filter(self, qs, location):
        location_type, location_id = location.split("|")
        location_id = int(location_id)

        if location_type == "country":
            return self.filter_by_country(qs, location_id)

        if location_type == "region":
            return self.filter_by_region(qs, location_id)

        if location_type == "city":
            return self.filter_by_city(qs, location_id)

    def filter_by_country(self, qs, id):
        return qs.filter(event__venue__country__id=id)

    def filter_by_region(self, qs, id):
        return qs.filter(Q(event__venue__city__region__id=id) | Q(event__venue__city__subregion__id=id))

    def filter_by_city(self, qs, id):
        return qs.filter(event__venue__city__id=id)


class SearchFilter(Filter):
    def search_tags(self, search_string):
        if search_string:
            return [{
                "name": search_string,
                "remove_url": "?" + self.parent.url_query(exclude="search")
            }]
        else:
            return None


    def filter(self, qs, search_string):
        # Use limits for ids query for optimization
        ids = SingleEvent.future_events.filter( 
            event__tagged_items__tag__name=search_string 
        ).annotate(
            repeat_count=Count('id') 
        ).values_list("id", flat=True)

        ids_string = ",".join([str(id) for id in ids])

        where = """
            (setweight(to_tsvector('pg_catalog.english', coalesce("event_event"."name", "event_event"."description")), 'D')) @@ plainto_tsquery('pg_catalog.english', %s)
            OR (setweight(to_tsvector('pg_catalog.english', coalesce("event_singleevent"."description", '')), 'D')) @@ plainto_tsquery('pg_catalog.english', %s)
        """

        if ids:
            ids_string = ",".join([str(id) for id in ids])
            where = """"event_singleevent"."id" IN ("""+ids_string+""") OR """ +where

        return qs.extra(
            where=[where],
            params=[search_string, search_string]
        ).annotate(Count("id"))


class NightLifeFilter(Filter):
    def __init__(self, name):
        self.name = name

    def search_tags(self, value):
        if value:
            return [{
                "name": "Night Life",
                "remove_url": "?" + self.parent.url_query(exclude="night_life")
            }]
        else:
            return None

    def filter(self, qs, value=None):
        return qs.filter(event__venue__venueaccount__types=VenueType.active_types.get(name="Nightclub"))


class EventFilter(object):
    def __init__(self, data, queryset=Event.events.all(), account=None):
        self.data = data.copy()
        self.queryset = queryset
        self.filters = {
            "start_date": DateFilter("start_date", "start_time", lookup="gte"),
            "end_date": DateFilter("end_date", "start_time", lookup="lte"),
            "start_time": TimeFilter("start_time", "start_time", lookup="gte"),
            "end_time": TimeFilter("end_time", "start_time", lookup="lte"),
            "tag": TagsFilter("tag", "tags"),
            "featured": Filter("featured", "featured"),
            "function": FunctionFilter("function", account=account),
            "search": SearchFilter("search", "search_index"),
            "location": LocationFilter("location")
        }

        self.filters["period"] = PeriodFilter("period", self.filters["start_date"], self.filters["end_date"])

        for key, queryFilter in self.filters.iteritems():
            queryFilter.parent = self

    def qs(self):
        qs = self.queryset
        for key, queryFilter in self.filters.iteritems():
            if self.data.get(key):
                qs = queryFilter.filter(qs, queryFilter.filter_data(self.data))
        return qs

    def objects_list(self):
        return list(self.qs())


    def url_query(self, **kwargs):
        data = self.data.copy()
        if "shortcut" in kwargs:
            return self.shortcut_url_query(kwargs["shortcut"])
        if "exclude" in kwargs:
            data = self.exclude(data, kwargs["exclude"])

        for key in kwargs:
            if key in self.filters:
                data[key] = self.filters[key].upgrade_value(data, kwargs[key])

        query_list = [self.filters[key].url_query(data) for key, value in data.iteritems() if value and key in self.filters]
        return "&".join(query_list)

    def exclude(self, data, keys):
        for key in keys.split("|"):
            if key in exclude_shortcuts:
                for key2 in exclude_shortcuts[key]:
                    if key2 in data:
                        del data[key2]
            else:
                if key in data:
                    del data[key]

        return data

    def shortcut_url_query(self, key):
        return getattr(self, "%s_shortcut" % key.replace("-", "_"))()

    def today_shortcut(self):
        today = datetime.datetime(*(datetime.date.today().timetuple()[:6]))
        start = today
        end = today.replace(hour=23, minute=59, second=59)

        return self.url_query(start_date=start, end_date=end)

    def tomorrow_shortcut(self):
        today = datetime.datetime(*(datetime.date.today().timetuple()[:6]))
        tomorrow = today + datetime.timedelta(days=1)
        start = tomorrow
        end = tomorrow.replace(hour=23, minute=59, second=59)

        return self.url_query(start_date=start, end_date=end)

    def this_weekend_shortcut(self):
        today = datetime.datetime(*(datetime.date.today().timetuple()[:6]))
        end = today + datetime.timedelta(days=6 - today.weekday())
        end = end.replace(hour=23, minute=59, second=59, microsecond=0)
        #sat is 5
        if today.weekday() == 5:
            start = today + datetime.timedelta(days=5 - today.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        #friday at 5pm is the weekend.
        else:
            start = today + datetime.timedelta(days=4 - today.weekday())
            start = start.replace(hour=17, minute=0, second=0, microsecond=0)

        return self.url_query(start_date=start, end_date=end)

    def next_week_shortcut(self):
        today = datetime.datetime(*(datetime.date.today().timetuple()[:6]))
        end = today + datetime.timedelta(days=13 - today.weekday())
        start = today + datetime.timedelta(days=7 - today.weekday())

        return self.url_query(start_date=start, end_date=end)

    def tags(self):
        return self.data.getlist("tag", [])

    def search_tags(self):
        tags = []
        for key, queryFilter in self.filters.iteritems():
            if self.data.get(key):
                new_tags = queryFilter.search_tags(queryFilter.filter_data(self.data))
                if new_tags:
                    tags += new_tags

        if self.data.get("start_date") and self.data.get("end_date"):
            start_date = dateparser.parse(self.data.get("start_date"))
            end_date = dateparser.parse(self.data.get("end_date"))

            if start_date==end_date.replace(hour=0, minute=0, second=0, microsecond=0):
                date_string = start_date.strftime("%b %d")
            else:
                date_string = "%s - %s" % (
                    start_date.strftime("%b %d"),
                    end_date.strftime("%b %d"),
                )

            tags += [{
                "name": date_string,
                "remove_url": "?" + self.url_query(exclude="start_date|end_date")
            }]

        if self.data.get("start_time") and self.data.get("end_time"):
            start_time = datetime.datetime.now().replace(hour=int(self.data.get("start_time")))            
            end_time = datetime.datetime.now().replace(hour=int(self.data.get("end_time")))

            tags += [{
                "name": "%s - %s" % (
                    start_time.strftime("%I %p"),
                    end_time.strftime("%I %p"),
                ),
                "remove_url": "?" + self.url_query(exclude="start_time|end_time")
            }]


        return tags
