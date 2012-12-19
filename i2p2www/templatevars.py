from flask import g, request, url_for

from i2p2www import CANONICAL_DOMAIN, app

I2P_TO_CLEAR = {
    'www.i2p2.i2p': 'www.i2p2.de',
    #'forum.i2p': 'forum.i2p2.de',
    'trac.i2p2.i2p': 'trac.i2p2.de',
    'mail.i2p': 'i2pmail.org',
    }


####################
# Template functions

@app.context_processor
def utility_processor():
    # Shorthand for getting a site url
    def get_site_url(path=None):
        lang = 'en'
        if hasattr(g, 'lang') and g.lang:
            lang = g.lang
        if path:
            return url_for('site_show', lang=lang, page=path)
        else:
            return url_for('site_show', lang=lang)

    # Shorthand for getting a language-specific url
    def get_url_with_lang(endpoint, **args):
        lang = 'en'
        if hasattr(g, 'lang') and g.lang:
            lang = g.lang
        return url_for(endpoint, lang=lang, **args)

    # Get a specific language flag, or the flag for the current language
    def get_flag(lang=None):
        if not lang:
            if hasattr(g, 'lang') and g.lang:
                lang = g.lang
            else:
                lang = 'en'
        return url_for('static', filename='images/flags/'+lang+'.png')

    # Provide the canonical link to the current page
    def get_canonical_link():
        protocol = request.url.split('//')[0]
        return protocol + '//' + CANONICAL_DOMAIN + request.path

    # Convert an I2P url to an equivalent clearnet one
    def convert_url_to_clearnet(value):
        if not value.endswith('.i2p'):
            # The url being passed in isn't an I2P url, so just return it
            return value
        if request.headers.get('X-I2P-Desthash') and not request.headers.get('X-Forwarded-Server'):
            # The request is from within I2P, so use I2P url
            return value
        # The request is either directly from clearnet or through an inproxy
        try:
            # Return the known clearnet url corresponding to the I2P url
            return I2P_TO_CLEAR[value]
        except KeyError:
            # The I2P site has no known clearnet address, so use an inproxy
            return value + '.to'

    # Convert a paginated URL to that of another page
    def url_for_other_page(page):
        args = request.view_args.copy()
        args['page'] = page
        return url_for(request.endpoint, **args)

    # Change the theme of the current page
    def change_theme(theme):
        args = {}
        if request.view_args:
            args = request.view_args.copy()
        args['theme'] = theme
        if request.endpoint:
            return url_for(request.endpoint, **args)
        # Probably a 404 error page
        return url_for('main_index', **args)

    return dict(i2pconv=convert_url_to_clearnet,
                url_for_other_page=url_for_other_page,
                change_theme=change_theme,
                site_url=get_site_url,
                get_url=get_url_with_lang,
                get_flag=get_flag,
                canonical=get_canonical_link)
