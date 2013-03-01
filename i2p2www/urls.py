from werkzeug.routing import BaseConverter

from i2p2www import app
from i2p2www.helpers import LazyView


#######################
# Custom URL converters

class LangConverter(BaseConverter):
    def __init__(self, url_map):
        super(LangConverter, self).__init__(url_map)
        self.regex = '(?:[a-z]{2})(-[a-z]{2})?'

    def to_python(self, value):
        parts = value.split('-')
        if len(parts) == 2:
            return parts[0] + '_' + parts[1].upper()
        return value

    def to_url(self, value):
        parts = value.split('_')
        if len(parts) == 2:
            return parts[0] + '-' + parts[1].lower()
        return value

app.url_map.converters['lang'] = LangConverter


######
# URLs

def url(url_rule, import_name, **options):
    view = LazyView('i2p2www.' + import_name)
    app.add_url_rule(url_rule, view_func=view, **options)

url('/', 'views.main_index')
url('/<lang:lang>/', 'views.site_show', defaults={'page': 'index'})
url('/<lang:lang>/<path:page>', 'views.site_show')

url('/<lang:lang>/blog/', 'blog.views.blog_index', defaults={'page': 1})
url('/<lang:lang>/blog/page/<int:page>', 'blog.views.blog_index')
url('/<lang:lang>/blog/category/<string:category>', 'blog.views.blog_index', defaults={'page': 1})
url('/<lang:lang>/blog/category/<string:category>/page/<int:page>', 'blog.views.blog_index')
url('/<lang:lang>/blog/post/<path:slug>', 'blog.views.blog_post')
url('/<lang:lang>/feed/blog/rss', 'blog.views.blog_rss')
url('/<lang:lang>/feed/blog/atom', 'blog.views.blog_atom')
url('/<lang:lang>/feed/blog/category/<string:category>/atom', 'blog.views.blog_atom')

url('/<lang:lang>/meetings/', 'meetings.views.meetings_index', defaults={'page': 1})
url('/<lang:lang>/meetings/page/<int:page>', 'meetings.views.meetings_index')
url('/<lang:lang>/meetings/<int:id>', 'meetings.views.meetings_show')
url('/<lang:lang>/meetings/<int:id>.log', 'meetings.views.meetings_show_log')
url('/<lang:lang>/meetings/<int:id>.rst', 'meetings.views.meetings_show_rst')
url('/<lang:lang>/feed/meetings/atom', 'meetings.views.meetings_atom')

url('/<lang:lang>/download', 'downloads.downloads_list')
url('/<lang:lang>/download/<path:file>', 'downloads.downloads_select')
url('/download/<string:protocol>/any/<path:file>', 'downloads.downloads_redirect', defaults={'mirror': None})
url('/download/<string:protocol>/<int:mirror>/<path:file>', 'downloads.downloads_redirect')

url('/meeting<int:id>', 'legacy.legacy_meeting')
url('/meeting<int:id>.html', 'legacy.legacy_meeting')
url('/status-<int:year>-<int:month>-<int:day>', 'legacy.legacy_status')
url('/status-<int:year>-<int:month>-<int:day>.html', 'legacy.legacy_status')
url('/<string:f>_<lang:lang>', 'legacy.legacy_show')
url('/<string:f>_<lang:lang>.html', 'legacy.legacy_show')
url('/<string:f>/', 'legacy.legacy_show')
url('/<string:f>.html', 'legacy.legacy_show')

url('/hosts.txt', 'views.hosts')
url('/robots.txt', 'views.robots')
url('/favicon.ico', 'views.favicon')

url('/googleadcf8b9c9f4ff24f.html', 'views.google')

url('/sitemap_index.xml', 'sitemap.render_sitemap_index')
url('/<lang:lang>/sitemap.xml', 'sitemap.render_sitemap')
