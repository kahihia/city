from models import Event
import datetime, time
from django.db.models import Q, Count


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
#        import pdb; pdb.set_trace()

        return qs.filter(event__tagged_items__tag__name__in=tags) \
            .annotate(repeat_count=Count('id')) \
            .filter(repeat_count=len(tags))

    def url_query(self, querydict):
        tags = querydict["tag"]
        if isinstance(tags, basestring):
            tags = [tags]
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


class BooleanFilter(Filter):
    pass


class FunctionFilter(Filter):
    def __init__(self, name):
        self.name = name
        pass

    def filter(self, qs, value):
        return getattr(self, "%s_filter" % value)(qs)

    def random_filter(self, qs):
        # qs.order_by = ['?']
        return qs.order_by("?")

    def tags_filter(self, qs):
        return qs

    def recently_featured_filter(self, qs):
        return qs.order_by("event__featured_on")

    def all_filter(self, qs):
        return qs

    def top_viewed_filter(self, qs):
        # TODO: add view statistic and sort by it
        return qs.order_by("-event__viewed_times")

    def latest_filter(self, qs):
        return qs.order_by("-event__created")

exclude_shortcuts = {
    "datetime": ["start_date", "end_date", "start_time", "end_time"]
}


class EventFilter(object):
    def __init__(self, data, queryset=Event.events.all()):
        self.data = data.copy()
        self.queryset = queryset
        self.filters = {
            "start_date": DateFilter("start_date", "start_time", lookup="gte"),
            "end_date": DateFilter("end_date", "start_time", lookup="lte"),
            "start_time": TimeFilter("start_time", "start_time", lookup="gte"),
            "end_time": TimeFilter("end_time", "start_time", lookup="lte"),
            "tag": TagsFilter("tag", "event__tags"),
            "featured": BooleanFilter("featured", "event__featured"),
            "function": FunctionFilter("function")
        }

    def qs(self):
        qs = self.queryset
        for key, queryFilter in self.filters.iteritems():
            if self.data.get(key):
                qs = queryFilter.filter(qs, queryFilter.filter_data(self.data))
        return self.select_first_days(qs)

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
