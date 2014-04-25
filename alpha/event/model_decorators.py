from easy_thumbnails.files import get_thumbnailer
from home.base import ModelDecorator


class EventModelDecorator(ModelDecorator):
    def sized_image(self, width=0, height=0):
        image_name = self._instance.image_name
        if image_name:
            thumbnailer = get_thumbnailer(image_name)
            thumbnail_options = {'crop': 'smart',
                                 'size': (width, height)}

            return thumbnailer.get_thumbnail(thumbnail_options).name
        else:
            return ''


class SingleEventModelDecorator(ModelDecorator):
    def date(self):
        return self._instance.start_time.strftime('%A, %B %d')

    def time(self):
        return self._instance.start_time.strftime('%I:%M %p')

    def price(self):
        if self._instance.price and self._instance.price != "$":
            return self._instance.price
        else:
            return 'Price not set'