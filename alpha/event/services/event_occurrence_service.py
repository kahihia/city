import json
import datetime
from event.models import SingleEvent
import dateutil.parser as dateparser


def update_occurrences(data, event):
    update_single_events(data, event)


def update_single_events(data, event):
    single_events = list(event.single_events.all())
    single_events_to_save_ids = []

    when_json = json.loads(data["when_json"])
    description_json = json.loads(data["description_json"])
    occurrences_json = json.loads(data["occurrences_json"])

    event.description = description_json['default']
    event.save()

    multiday_start_time = None
    multiday_end_time = None

    for year, months in when_json.iteritems():
        for month, days in months.iteritems():
            for day, times in days.iteritems():
                date = datetime.datetime(int(year), int(month), int(day), 0, 0)

                occurrences_day_key = date.strftime("%m/%d/%Y")

                if occurrences_day_key in occurrences_json:
                    occurrences = occurrences_json[occurrences_day_key]
                    start_key, end_key = "startTime", "endTime"
                else:
                    occurrences = [times]
                    start_key, end_key = "start", "end"

                for occurrence in occurrences:
                    start_time = dateparser.parse(occurrence[start_key])
                    start = datetime.datetime(int(year), int(month), int(day), start_time.hour, start_time.minute)

                    if not multiday_start_time or multiday_start_time > start:
                        multiday_start_time = start

                    end_time = dateparser.parse(occurrence[end_key])
                    end = datetime.datetime(int(year), int(month), int(day), end_time.hour, end_time.minute)

                    if not multiday_end_time or multiday_end_time < end:
                        multiday_end_time = end

                    if occurrences_day_key in description_json['days']:
                        description = description_json['days'][occurrences_day_key]
                    else:
                        description = ""                        


                    single_event = SingleEvent(
                        event=event,
                        start_time=start.strftime('%Y-%m-%d %H:%M'),
                        end_time=end.strftime('%Y-%m-%d %H:%M'),
                        description=description,
                        is_occurrence=(event.event_type=="MULTIDAY")
                    )

                    ext_single_event = get_identic_single_event_from_list(single_event, single_events)
                    if not ext_single_event:
                        single_event.save()
                    else:
                        single_event = ext_single_event
                        single_event.is_occurrence = (event.event_type=="MULTIDAY")
                        single_event.save()
                        single_events_to_save_ids.append(ext_single_event.id)

    if event.event_type=="MULTIDAY":
        single_event = SingleEvent(
            event=event,
            start_time=multiday_start_time.strftime('%Y-%m-%d %H:%M'),
            end_time=multiday_end_time.strftime('%Y-%m-%d %H:%M'),
            description=description,
            is_occurrence=False
        )

        ext_single_event = get_identic_single_event_from_list(single_event, single_events)
        if not ext_single_event:
            single_event.save()
        else:
            single_event = ext_single_event            
            single_events_to_save_ids.append(ext_single_event.id)

    single_events_to_delete_ids = list(set([item.id for item in single_events]).difference(single_events_to_save_ids))
    SingleEvent.objects.filter(id__in=single_events_to_delete_ids).delete()


def get_identic_single_event_from_list(single_event, single_event_list):
    for item in single_event_list:
        if item.start_time == dateparser.parse(single_event.start_time) \
            and item.end_time == dateparser.parse(single_event.end_time) \
                and item.description == single_event.description:
            return item

    return False


def prepare_initial_when_and_description_for_single_events(event, occurrences):
    when_json = {}
    description_json = {
        "default": event.description,
        "days": {}
    }

    for occurrence in occurrences:
        start_time = occurrence.start_time
        year = start_time.year
        month = start_time.month
        day = start_time.day

        if not year in when_json:
            when_json[year] = {}

        if not month in when_json[year]:
            when_json[year][month] = {}

        if not day in when_json[year][month]:
            # Only first day
            when_json[year][month][day] = {
                "start": start_time.strftime('%I:%M %p'),
                "end": occurrence.end_time.strftime('%I:%M %p')
            }

            description_json["days"][start_time.strftime("%m/%d/%Y")] = occurrence.description

    return (when_json, description_json)


def prepare_initial_when_and_description(event):
    if event.event_type=="MULTIDAY":
        single_events = SingleEvent.objects.filter(event=event, is_occurrence=True).order_by("start_time")
    else:
        single_events = SingleEvent.objects.filter(event=event, is_occurrence=False).order_by("start_time")
    
    return prepare_initial_when_and_description_for_single_events(event, single_events)


def prepare_initial_occurrences(event):
    if event.event_type=="MULTIDAY":
        single_events = SingleEvent.objects.filter(event=event, is_occurrence=True).order_by("start_time")
    else:
        single_events = SingleEvent.objects.filter(event=event, is_occurrence=False).order_by("start_time")

    occurrences_json = {}

    for single_event in single_events:
        occurrences_day_key = single_event.start_time.strftime("%m/%d/%Y")

        if occurrences_day_key in occurrences_json:
            occurrences_json[occurrences_day_key].append({
                "startTime": single_event.start_time.strftime('%I:%M %p'),
                "endTime": single_event.end_time.strftime('%I:%M %p')
            })
        else:
            occurrences_json[occurrences_day_key] = []
        
    return occurrences_json
