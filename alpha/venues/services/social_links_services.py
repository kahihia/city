import json

def prepare_social_links(venue_account):
    social_links_json = {
        "social_links": map(lambda socialLinkModel: {
                "title": socialLinkModel.title,
                "url": socialLinkModel.link
            }, venue_account.social_links)
    }
    
    return json.dumps(social_links_json)	