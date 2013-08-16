from services.location_service import user_location


class LocationMiddleware(object):
    def process_request(self, request):
        request.user_location = user_location(request)
