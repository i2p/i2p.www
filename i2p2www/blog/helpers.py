import codecs
import datetime
from docutils.core import publish_parts
from flask import abort, g, render_template_string, safe_join, url_for
import os
import os.path

from i2p2www import BLOG_DIR


SUPPORTED_METATAGS = {
    'author': u'I2P devs',
    'category': None,
    'date': None,
    'excerpt': u'',
    }

LIST_METATAGS = [
    'category',
    ]


#####################
# Blog helper methods

def get_blog_feed_items(num=0, category=None):
    posts = get_blog_posts(num, True, category=category)
    items = []
    for post in posts:
        meta = post[1]
        parts = post[2]
        a = {}
        a['title'] = meta['title']
        a['content'] = meta['excerpt'] if len(meta['excerpt']) > 0 else parts['fragment']
        a['url'] = url_for('blog_post', lang=g.lang, slug=post[0])
        a['updated'] = datetime.datetime.strptime(meta['date'], '%Y-%m-%d')
        items.append(a)
    return items

def get_blog_posts(num=0, return_parts=False, category=None):
    """
    Returns the latest #num valid posts sorted by date, or all slugs if num=0.
    """
    slugs = get_blog_slugs(num)
    posts= []
    for slug in slugs:
        parts = render_blog_post(slug)
        if parts:
            meta = get_metadata_from_meta(parts['meta'])
            meta['date'] = meta['date'] if meta['date'] else get_date_from_slug(slug)
            meta['title'] = parts['title']
            if not category or (meta['category'] and category in meta['category']):
                if return_parts:
                    posts.append((slug, meta, parts))
                else:
                    posts.append((slug, meta))
    return posts

def get_blog_slugs(num=0):
    """
    Returns the latest #num valid slugs sorted by date, or all slugs if num=0.
    """
    # list of slugs
    slugs=[]
    # walk over all directories/files
    for v in os.walk(BLOG_DIR):
        # iterate over all files
        slugbase = os.path.relpath(v[0], BLOG_DIR)
        for f in v[2]:
            # ignore all non-.rst files
            if not f.endswith('.rst'):
                continue
            slugs.append(safe_join(slugbase, f[:-4]))
    slugs.sort()
    slugs.reverse()
    if (num > 0):
        return slugs[:num]
    return slugs

def get_date_from_slug(slug):
    parts = slug.split('/')
    return "%s-%s-%s" % (parts[0], parts[1], parts[2])

def render_blog_post(slug):
    """
    Render the blog post
    TODO:
    - caching
    - move to own file
    """
    # check if that file actually exists
    path = safe_join(BLOG_DIR, slug + ".rst")
    if not os.path.exists(path):
        abort(404)

    # read file
    with codecs.open(path, encoding='utf-8') as fd:
        content = fd.read()

    # render the post with Jinja2 to handle URLs etc.
    rendered_content = render_template_string(content)

    # publish the post with docutils
    return publish_parts(source=rendered_content, source_path=BLOG_DIR, writer_name="html")

def get_metadata_from_meta(meta):
    metaLines = meta.split('\n')
    ret = {}
    for metaTag in SUPPORTED_METATAGS:
        metaLine = [s for s in metaLines if 'name="%s"' % metaTag in s]
        ret[metaTag] = metaLine[0].split('content="')[1].split('"')[0] if len(metaLine) > 0 else SUPPORTED_METATAGS[metaTag]
        if metaTag in LIST_METATAGS and ret[metaTag]:
            ret[metaTag] = [s.strip() for s in ret[metaTag].split(',')]
    return ret
