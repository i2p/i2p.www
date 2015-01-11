from flask import abort, render_template, request
from werkzeug.contrib.atom import AtomFeed

from i2p2www import BLOG_DIR, BLOG_POSTS_PER_FEED, BLOG_POSTS_PER_PAGE, cache
from i2p2www.blog.helpers import get_blog_posts, get_blog_feed_items, get_date_from_slug, get_metadata_from_meta, render_blog_post
from i2p2www.helpers import Pagination, get_for_page


############
# Blog views

@cache.memoize(600)
def blog_index(page, category=None):
    all_posts = get_blog_posts(category=category)
    posts = get_for_page(all_posts, page, BLOG_POSTS_PER_PAGE)
    if not posts and page != 1:
        abort(404)
    pagination = Pagination(page, BLOG_POSTS_PER_PAGE, len(all_posts))
    if category:
        return render_template('blog/category.html', pagination=pagination, posts=posts, category=category)
    else:
        return render_template('blog/index.html', pagination=pagination, posts=posts)

@cache.memoize(600)
def blog_post(slug):
    # try to render that blog post.. throws 404 if it does not exist
    parts = render_blog_post(slug)

    if parts:
        meta = get_metadata_from_meta(parts['meta'])
        meta['date'] = meta['date'] if meta['date'] else get_date_from_slug(slug)
        # add notification to any error messages
        parts['fragment'] = parts['fragment'].replace('Docutils System Messages', 'There are errors in this translation. Please comment on <a href="https://trac.i2p2.de/ticket/1396">this ticket</a> with the URL of this page.')
        # remove BLOG_DIR from any error messages
        parts['fragment'] = parts['fragment'].replace(BLOG_DIR, 'Blog')
        # now just pass to simple template file and we are done
        return render_template('blog/post.html', parts=parts, title=parts['title'], body=parts['fragment'], slug=slug, meta=meta)
    else:
        abort(404)

def blog_rss():
    # TODO: implement
    pass

@cache.cached(600)
def blog_atom(category=None):
    feed_title = 'I2P Blog'
    if category:
        feed_title = 'I2P Blog Category: %s' % category
    feed = AtomFeed(feed_title, feed_url=request.url, url=request.url_root)
    items = get_blog_feed_items(BLOG_POSTS_PER_FEED, category=category)
    for item in items:
        feed.add(item['title'],
                 item['content'],
                 content_type='html',
                 url=item['url'],
                 updated=item['updated'])
    return feed.get_response()
