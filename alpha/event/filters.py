from models import Event, Venue
import datetime
import re
import string
import nltk
from accounts.models import VenueType
from django.db.models import Q
from cities.models import Region, City


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

    def search_tags(self):
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

        where = 'EXTRACT(hour from %s) %s %s' % (self.field.replace("single_events__", "event_singleevent."), operation, value)

        return qs.extra(where=[where])


class TagsFilter(Filter):
    def filter(self, qs, tags):
        return qs.filter(tagged_items__tag__name__in=tags)

    def url_query(self, querydict):
        tags = querydict["tag"]
        if isinstance(tags, basestring):
            tags = querydict.getlist(self.name)
        return "&".join(["tag=%s" % tag for tag in tags])

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
    "family": "Family"
}


class FunctionFilter(Filter):
    def __init__(self, name):
        self.name = name

    def filter(self, qs, value):
        return getattr(self, "%s_filter" % value)(qs)

    def random_filter(self, qs):
        # qs.order_by = ['?']
        return qs.order_by("?")

    def tags_filter(self, qs):
        return qs

    def recently_featured_filter(self, qs):
        return qs.filter(featuredevent__isnull=False).order_by("featuredevent__start_time")

    def all_filter(self, qs):
        return qs

    def top_viewed_filter(self, qs):
        # TODO: add view statistic and sort by it
        return qs.order_by("-viewed_times")

    def latest_filter(self, qs):
        return qs.order_by("-created")

    def night_life_filter(self, qs):
        return qs.filter(
            Q(tagged_items__tag__name__in=["19+", "Night Life", "DJ", "Party", "Rave"]) | Q(venue__venueaccount__types=VenueType.active_types.get(name="Nightlife & Singles"))
        )

    def date_night_filter(self, qs):
        return qs.filter(tagged_items__tag__name__in=["Date Night"])

    def free_filter(self, qs):
        ids = qs.extra(
            where=["""
                event_singleevent.search_index @@ plainto_tsquery('pg_catalog.english', 'free')
                OR event_event.search_index @@ plainto_tsquery('pg_catalog.english', 'free')
            """]
        ).values_list("id", flat=True)

        return qs.filter(Q(tagged_items__tag__name__in=["Free"]) | Q(id__in=list(ids)))

    def family_filter(self, qs):
        ids = qs.extra(
            where=["""
                event_singleevent.search_index @@ plainto_tsquery('pg_catalog.english', 'family')
                OR event_event.search_index @@ plainto_tsquery('pg_catalog.english', 'family')
            """]
        ).values_list("id", flat=True)

        return qs.filter(Q(tagged_items__tag__name__in=["Family"]) | Q(id__in=list(ids)))

    def search_tags(self, function):
        name = search_tags_for_filters.get(function)
        print name
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
        return qs.filter(venue__country__id=id)

    def filter_by_region(self, qs, id):
        return qs.filter(Q(venue__city__region__id=id) | Q(venue__city__subregion__id=id))

    def filter_by_city(self, qs, id):
        return qs.filter(venue__city__id=id)


class SearchFilter(Filter):
    def search_tags(self, search_string):
        # TODO: use nslt to split words
        search_string = search_string.strip()
        if search_string:
            return [{
                "name": word,
                "remove_url": "?" + self.parent.url_query(search=search_string.replace(word, ""))
            } for word in nltk.word_tokenize(
                re.sub('[%s]' % re.escape(string.punctuation), '', search_string)
            )]
        else:
            return None

    def filter(self, qs, search_string):
        return qs.extra(
            where=["""
                event_singleevent.search_index @@ plainto_tsquery('pg_catalog.english', %s)
                OR event_event.search_index @@ plainto_tsquery('pg_catalog.english', %s)
            """],
            params=[search_string, search_string]
        )


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
        return qs.filter(venue__venueaccount__types=VenueType.active_types.get(name="Nightclub"))


class EventFilter(object):
    def __init__(self, data, queryset=Event.events.all()):
        self.data = data.copy()
        self.queryset = queryset
        self.filters = {
            "start_date": DateFilter("start_date", "single_events__start_time", lookup="gte"),
            "end_date": DateFilter("end_date", "single_events__start_time", lookup="lte"),
            "start_time": TimeFilter("start_time", "single_events__start_time", lookup="gte"),
            "end_time": TimeFilter("end_time", "single_events__start_time", lookup="lte"),
            "tag": TagsFilter("tag", "tags"),
            "featured": Filter("featured", "featured"),
            "function": FunctionFilter("function"),
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

    def select_first_days(self, qs):
        days = qs.values_list("id", flat=True)
        if days:
            return qs.extra(where=["""ROW("event_singleevent"."event_id", "event_singleevent"."start_time") IN (SELECT event_id, MIN(start_time) FROM event_singleevent WHERE id IN (%s) GROUP BY event_id)"""
                % ",".join([str(id) for id in days])])
        return qs

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
        return tags
