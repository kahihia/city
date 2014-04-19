from home.base import ModelDecorator


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