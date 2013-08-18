

def found_dublicates(Venue):
    for venue in Venue.objects.all():   
        dublicates = Venue.objects.filter(name=venue.name, street=venue.street, city=venue.city, country=venue.country)
        if dublicates.count()>1:
            return dublicates

def relink_events(dublicates):
    original = dublicates[0]
    dublicates = dublicates[1:]

    for venue in dublicates:
        for event in venue.event_set.all():
            event.venue = original
            event.save()

    for venue in dublicates:
        venue.delete()



