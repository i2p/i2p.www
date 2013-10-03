from flask import abort, redirect, render_template, safe_join, send_from_directory, url_for
import os.path

from i2p2www import STATIC_DIR, TEMPLATE_DIR
from i2p2www.blog.helpers import get_blog_posts


#######################
# General page handlers

# Index - redirects to en homepage
def main_index():
    return redirect(url_for('site_show', lang='en'))

# Site pages
def site_show(page):
    if page.endswith('.html'):
        return redirect(url_for('site_show', page=page[:-5]))
    name = 'site/%s.html' % page
    page_file = safe_join(TEMPLATE_DIR, name)

    if not os.path.exists(page_file):
        # Could be a directory, so try index.html
        name = 'site/%s/index.html' % page
        page_file = safe_join(TEMPLATE_DIR, name)
        if not os.path.exists(page_file):
            # bah! those damn users all the time!
            abort(404)

    options = {
        'page': page,
        }
    if (page == 'index'):
        options['blog_posts'] = get_blog_posts(8)

    # hah!
    return render_template(name, **options)


############
# Root files

def hosts():
    return send_from_directory(STATIC_DIR, 'hosts.txt', mimetype='text/plain')

def robots():
    return send_from_directory(STATIC_DIR, 'robots.txt', mimetype='text/plain')

def favicon():
    return send_from_directory(STATIC_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


#######################################
# Verification pages for search engines

def google():
    return send_from_directory(STATIC_DIR, 'googleadcf8b9c9f4ff24f.html')

def bing():
    return send_from_directory(STATIC_DIR, 'BingSiteAuth.xml', mimetype='application/xml')
