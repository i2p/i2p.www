from flask import abort, render_template, request
from werkzeug.contrib.atom import AtomFeed

from i2p2www import BLOG_ENTRIES_PER_PAGE
from i2p2www.blog.helpers import get_blog_entries, get_blog_feed_items, render_blog_entry
from i2p2www.helpers import Pagination, get_for_page


############
# Blog views

def blog_index(page):
    all_entries = get_blog_entries()
    entries = get_for_page(all_entries, page, BLOG_ENTRIES_PER_PAGE)
    if not entries and page != 1:
        abort(404)
    pagination = Pagination(page, BLOG_ENTRIES_PER_PAGE, len(all_entries))
    return render_template('blog/index.html', pagination=pagination, entries=entries)

def blog_entry(slug):
    # try to render that blog entry.. throws 404 if it does not exist
    parts = render_blog_entry(slug)

    if parts:
        # now just pass to simple template file and we are done
        return render_template('blog/entry.html', parts=parts, title=parts['title'], body=parts['fragment'], slug=slug)
    else:
        abort(404)

def blog_rss():
    # TODO: implement
    pass

def blog_atom():
    # TODO: Only output beginning of each blog entry
    feed = AtomFeed('I2P Blog', feed_url=request.url, url=request.url_root)
    items = get_blog_feed_items(10)
    for item in items:
        feed.add(item['title'],
                 item['content'],
                 content_type='html',
                 url=item['url'],
                 updated=item['updated'])
    return feed.get_response()
