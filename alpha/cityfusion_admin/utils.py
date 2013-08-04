from django_facebook.api import get_persistent_graph
from event.models import FacebookEvent


def run_async(func):
    """
        run_async(func)
            function decorator, intended to make "func" run in a separate
            thread (asynchronously).
            Returns the created Thread object

            E.g.:
            @run_async
            def task1():
                do_something

            @run_async
            def task2():
                do_something_too

            t1 = task1()
            t2 = task2()
            ...
            t1.join()
            t2.join()
    """
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target = func, args = args, kwargs = kwargs)
        func_hl.start()
        return func_hl

    return async_func


def get_facebook_events_data(request, place, page):
    paging_delta = 100

    fb = get_persistent_graph(request)
    params = {
        'q': place,
        'type': 'event',
        'fields': 'id,name,picture,start_time,end_time,location,venue',
        'limit': paging_delta
    }

    if page:
        params['offset'] = page * paging_delta

    result = fb.get('search', **params)
    events = FacebookEvent.prepare_events(result['data'])

    return {
        'events': events,
        'page': (page + 1) if len(result['data']) == paging_delta else 0
    };