import json
import re
from htmlentitydefs import name2codepoint
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


def shorten_string(value, length):
    if len(value) > length:
        return '%s...' % value[:length]

    return value


def htmldecode(text):
        """Decode HTML entities in the given text."""
        if type(text) is unicode:
                uchr = unichr
        else:
                uchr = lambda value: value > 255 and unichr(value) or chr(value)

        def entitydecode(match, uchr=uchr):
                entity = match.group(1)
                if entity.startswith('#x'):
                        return uchr(int(entity[2:], 16))
                elif entity.startswith('#'):
                        return uchr(int(entity[1:]))
                elif entity in name2codepoint:
                        return uchr(name2codepoint[entity])
                else:
                        return match.group(0)
        text = text.replace('&nbsp;', '')
        charrefpat = re.compile(r'&(#(\d+|x[\da-fA-F]+)|[\w.:-]+);?')
        return charrefpat.sub(entitydecode, text)