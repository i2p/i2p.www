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

lazy_views = {}

def url(url_rule, import_name, **options):
    if import_name in lazy_views:
        view = lazy_views[import_name]
    else:
        view = LazyView('i2p2www.' + import_name)
        lazy_views[import_name] = view
    app.add_url_rule(url_rule, view_func=view, **options)

url('/', 'views.main_index')
url('/<lang:lang>/', 'views.site_show', defaults={'page': 'index'})
url('/<lang:lang>/<path:page>', 'views.site_show')

url('/spec', 'spec.views.spec_index')
url('/spec/<string:name>', 'spec.views.spec_show')
url('/spec/<string:name>.txt', 'spec.views.spec_show_txt')
url('/spec/proposals', 'spec.views.proposal_index')
url('/spec/proposals/<int:number>', 'spec.views.proposal_number')
url('/spec/proposals/<string:name>', 'spec.views.proposal_show')
url('/spec/proposals/<string:name>.txt', 'spec.views.proposal_show_txt')

url('/<lang:lang>/papers/', 'anonbib.views.papers_list')
url('/<lang:lang>/papers/bibtex', 'anonbib.views.papers_bibtex')
url('/<lang:lang>/papers/by-<string:choice>', 'anonbib.views.papers_list')
url('/<lang:lang>/papers/tag/<string:tag>/', 'anonbib.views.papers_list')
url('/<lang:lang>/papers/tag/<string:tag>/bibtex', 'anonbib.views.papers_bibtex')
url('/<lang:lang>/papers/tag/<string:tag>/by-<string:choice>', 'anonbib.views.papers_list')

url('/<lang:lang>/blog/', 'blog.views.blog_index', defaults={'page': 1})
url('/<lang:lang>/blog/page/<int:page>', 'blog.views.blog_index')
url('/<lang:lang>/blog/category/<string:category>', 'blog.views.blog_index', defaults={'page': 1})
url('/<lang:lang>/blog/category/<string:category>/page/<int:page>', 'blog.views.blog_index')
url('/<lang:lang>/blog/post/<path:slug>', 'blog.views.blog_post')
url('/<lang:lang>/feed/blog/rss', 'blog.views.blog_rss')
url('/<lang:lang>/feed/blog/atom', 'blog.views.blog_atom')
url('/<lang:lang>/feed/blog/category/<string:category>/atom', 'blog.views.blog_atom')
url('/b/<string:shortlink>', 'blog.views.blog_post_shortlink')

url('/<lang:lang>/meetings/', 'meetings.views.meetings_index', defaults={'page': 1})
url('/<lang:lang>/meetings/page/<int:page>', 'meetings.views.meetings_index')
url('/<lang:lang>/meetings/<int:id>', 'meetings.views.meetings_show')
url('/<lang:lang>/meetings/<int:id>.log', 'meetings.views.meetings_show_log')
url('/<lang:lang>/meetings/<int:id>.rst', 'meetings.views.meetings_show_rst')
url('/<lang:lang>/feed/meetings/atom', 'meetings.views.meetings_atom')

url('/<lang:lang>/browser', 'browser.browser_frontpage')
url('/<lang:lang>/browser/intro', 'browser.browser_intro')
url('/<lang:lang>/browser/faq', 'browser.browser_faq')
url('/<lang:lang>/browser/known_issues', 'browser.browser_known_issues')
url('/<lang:lang>/browser/troubleshooting', 'browser.browser_troubleshooting')
url('/<lang:lang>/browser/releasenotes', 'browser.browser_releasenotes')
url('/<lang:lang>/browser/updating', 'browser.browser_updating')
url('/<lang:lang>/browser/download', 'browser.browser_download')

url('/<lang:lang>/download', 'downloads.downloads_list')
url('/<lang:lang>/download/debian', 'downloads.downloads_debian')
url('/<lang:lang>/download/firefox', 'downloads.downloads_firefox')
url('/<lang:lang>/download/lab', 'downloads.downloads_lab')
url('/<lang:lang>/download/<string:version>/<path:file>/mirrors', 'downloads.downloads_select')
url('/<lang:lang>/download/<string:version>/<string:net>/any/<path:file>/download', 'downloads.downloads_redirect', defaults={'protocol': None, 'domain': None})
url('/<lang:lang>/download/<string:version>/<string:net>/<string:protocol>/any/<path:file>/download', 'downloads.downloads_redirect', defaults={'domain': None})
url('/<lang:lang>/download/<string:version>/<string:net>/<string:protocol>/<string:domain>/<path:file>/download', 'downloads.downloads_redirect')

url('/meeting<int:id>', 'legacy.legacy_meeting')
url('/meeting<int:id>.html', 'legacy.legacy_meeting')
url('/status-<int:year>-<int:month>-<int:day>', 'legacy.legacy_status')
url('/status-<int:year>-<int:month>-<int:day>.html', 'legacy.legacy_status')
url('/release-<string:version>_<lang:lang>', 'legacy.legacy_release')
url('/release-<string:version>_<lang:lang>.html', 'legacy.legacy_release')
url('/release-<string:version>/', 'legacy.legacy_release')
url('/release-<string:version>.html', 'legacy.legacy_release')
url('/<string:f>_<lang:lang>', 'legacy.legacy_show')
url('/<string:f>_<lang:lang>.html', 'legacy.legacy_show')
url('/<string:f>/', 'legacy.legacy_show')
url('/<string:f>.html', 'legacy.legacy_show')
url('/<string:f>.txt', 'legacy.legacy_show')

url('/hosts.txt', 'views.hosts')
url('/robots.txt', 'views.robots')
url('/favicon.ico', 'views.favicon')

url('/googleadcf8b9c9f4ff24f.html', 'views.google')
url('/BingSiteAuth.xml', 'views.bing')

url('/sitemap_index.xml', 'sitemap.render_sitemap_index')
url('/<lang:lang>/sitemap.xml', 'sitemap.render_sitemap')
