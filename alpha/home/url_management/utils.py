from .registry import url_management_registry


def url_by_identifier(identifier):
    for url_rule in url_management_registry:
        url = url_rule.create_url(identifier)
        if url:
            return url
    return ''