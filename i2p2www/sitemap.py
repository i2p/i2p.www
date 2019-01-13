from flask import g, make_response, render_template, request, safe_join
import os.path

from i2p2www import SITE_DIR, SUPPORTED_LANGS, cache
from i2p2www.blog.helpers import get_blog_slugs
from i2p2www.meetings.helpers import get_meetings_ids


def to_url(value):
    parts = value.split('_')
    if len(parts) == 2:
        return parts[0] + '-' + parts[1].lower()
    return value


LANG_FRAGS = []
for lang in SUPPORTED_LANGS:
    LANG_FRAGS.append(to_url(lang))


##########
# Sitemaps

def get_sitemap_cache_key():
    return 'view/%s/%s' % (request.url_root, request.path)

@cache.cached(600, get_sitemap_cache_key)
def render_sitemap_index():
    # Include the / at the end, so the language can be
    # sandwiched between url_root and /sitemap.xml in
    # the template.
    url_root = request.url_root

    # Render and return the sitemap index
    response = make_response(render_template('global/sitemap_index.xml', url_root=url_root, langs=LANG_FRAGS))
    response.headers['Content-Type'] = 'application/xml'
    return response

@cache.cached(600, get_sitemap_cache_key)
def render_sitemap():
    # Include the / at the end, so the language can be
    # sandwiched between url_root and url.path in the
    # template.
    url_root = request.url_root
    urls = []

    # --------------
    # Main site urls
    # --------------
    # walk over all directories/files
    for v in os.walk(SITE_DIR):
        # iterate over all files
        pathbase = os.path.relpath(v[0], SITE_DIR)
        for f in v[2]:
            # ignore all non-.html files
            if not f.endswith('.html'):
                continue
            path = pathbase
            if f != 'index.html':
                path = safe_join(pathbase, f[:-5])
            if path.startswith('.'):
                path = path[1:]
            if not path.startswith('/'):
                path = '/%s' % path
            urls.append({
                'path': path,
                })

    # -----------
    # Papers urls
    # -----------
    urls.append({
        'path': '/papers/',
        })
    urls.append({
        'path': '/papers/bibtex',
        })

    # ---------
    # Blog urls
    # ---------
    urls.append({
        'path': '/blog/',
        })
    blog_slugs = get_blog_slugs()
    for slug in blog_slugs:
        urls.append({
            'path': '/blog/post/%s' % slug,
            })

    # -------------
    # Meetings urls
    # -------------
    urls.append({
        'path': '/meetings/',
        })
    meetings = get_meetings_ids()
    for id in meetings:
        urls.append({
            'path': '/meetings/%d' % id,
            })

    # --------------
    # Downloads urls
    # --------------
    urls.append({
        'path': '/download',
        })
    urls.append({
        'path': '/download/debian',
        })
    urls.append({
        'path': '/download/firefox',
        })

    # Render and return the sitemap
    response = make_response(render_template('global/sitemap.xml', url_root=url_root, langs=LANG_FRAGS,
                                             curlang=to_url(g.lang), urls=urls))
    response.headers['Content-Type'] = 'application/xml'
    return response
