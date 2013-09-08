import json
from django.core.serializers import deserialize


def deserialize_json_deep(data, relations={}):
    objects = []
    if type(data) in [str, unicode]:
        data = json.loads(data)

    is_single = (type(data) != list)
    if is_single:
        data = [data]

    for item in data:
        related_items = {}
        for rel in relations:
            if rel in item['fields']:
                related_items[rel] = item['fields'][rel]
                del item['fields'][rel]

        obj = list(deserialize('json', json.dumps([item])))[0].object
        for rel in related_items:
            rel_value = relations[rel]['relations'] if (type(relations) == dict
                                                    and 'relations' in relations[rel]) else {}
            setattr(obj, rel, deserialize_json_deep(related_items[rel], rel_value))

        objects.append(obj)
    return objects[0] if is_single else objects