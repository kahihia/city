import datetime


def find_nearest_city(cities, location):
    return cities.distance(location).order_by('distance')[0]


def get_dates_from_request(request):
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)

    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    else:
        start_date = datetime.datetime.now()

    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
    else:
        end_date = datetime.datetime.now()

    return start_date, end_date


def get_times_from_request(request):
    start_time = request.GET.get("start_time", 13)
    end_time = request.GET.get("end_time", 20)
    return start_time, end_time
