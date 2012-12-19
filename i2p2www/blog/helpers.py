import codecs
import datetime
from docutils.core import publish_parts
from flask import abort, g, safe_join, url_for
import os
import os.path

from i2p2www import BLOG_DIR


#####################
# Blog helper methods

def get_blog_feed_items(num=0):
    entries = get_blog_entries(num)
    items = []
    for entry in entries:
        parts = render_blog_entry(entry[0])
        if parts:
            a = {}
            a['title'] = parts['title']
            a['content'] = parts['fragment']
            a['url'] = url_for('blog_entry', lang=g.lang, slug=entry[0])
            a['updated'] = datetime.datetime.strptime(entry[1], '%Y-%m-%d')
            items.append(a)
    return items

def get_blog_entries(num=0):
    """
    Returns the latest #num valid entries sorted by date, or all slugs if num=0.
    """
    slugs = get_blog_slugs(num)
    entries= []
    for slug in slugs:
        date = get_date_from_slug(slug)
        titlepart = slug.rsplit('/', 1)[1]
        title = ' '.join(titlepart.split('_'))
        entries.append((slug, date, title))
    return entries

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

def render_blog_entry(slug):
    """
    Render the blog entry
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

    return publish_parts(source=content, source_path=BLOG_DIR, writer_name="html")
