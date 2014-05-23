from flask import g, redirect, url_for


############
# Shortcodes
#
# Two-letter shortcodes are not allowed, they clash with language codes

SHORTCODES={
    'd':    {'function': 'downloads_list',   'params': {}},
    'get':  {'function': 'downloads_list',   'params': {}},
}

##############
# Legacy paths

LEGACY_FUNCTIONS_MAP={
    'announcements': {'function': 'blog_index',       'params': {}},
    'debian':        {'function': 'downloads_debian', 'params': {}},
    'download':      {'function': 'downloads_list',   'params': {}},
    'installation':  {'function': 'downloads_list',   'params': {}},
    'meetings':      {'function': 'meetings_index',   'params': {}},
    'papers':        {'function': 'papers_list',      'params': {}},
    'statusnotes':   {'function': 'blog_index',       'params': {}},
}

LEGACY_PAGES_MAP={
    'api':                    'docs',
    'applications':           'get-involved/develop/applications',
    'benchmarks':             'misc/benchmarks',
    'bittorrent':             'docs/applications/bittorrent',
    'blockfile':              'docs/spec/blockfile',
    'bob':                    'docs/api/bob',
    'bounties':               'get-involved/bounties',
    'bounty_arabic':          'get-involved/bounties/arabic-trans',
    'bounty_btcclient':       'get-involved/bounties/btc-client',
    'bounty_datastore':       'get-involved/bounties/datastore',
    'bounty_debpack':         'get-involved/bounties/deb-pack',
    'bounty_i2phex':          'get-involved/bounties/i2phex',
    'bounty_ipv6':            'get-involved/bounties/ipv6',
    'bounty_netdb':           'get-involved/bounties/netdb',
    'bounty_rutrans':         'get-involved/bounties/russian-trans',
    'bounty_silc':            'get-involved/bounties/silc',
    'bounty_syndie2012':      'get-involved/bounties/syndie-2012',
    'bounty_unittests':       'get-involved/bounties/unit-tests',
    'bounty_vuzeplugin':      'get-involved/bounties/vuze-plugin',
    'clt':                    'misc/clt',
    'common_structures_spec': 'docs/spec/common-structures',
    'configuration':          'docs/spec/configuration',
    'contact':                'contact',
    'cvs':                    'misc/cvs',
    'datagrams':              'docs/api/datagrams',
    'dev-guidelines':         'get-involved/guides/dev-guidelines',
    'developerskeys':         'get-involved/develop/developers-keys',
    'donate':                 'get-involved/donate',
    'getinvolved':            'get-involved',
    'geoip':                  'docs/spec/geoip',
    'glossary':               'about/glossary',
    'halloffame':             'about/hall-of-fame',
    'how':                    'docs',
    'how_cryptography':       'docs/how/cryptography',
    'how_elgamalaes':         'docs/how/elgamal-aes',
    'how_garlicrouting':      'docs/how/garlic-routing',
    'how_intro':              'docs/how/intro',
    'how_networkcomparisons': 'comparison',
    'how_networkdatabase':    'docs/how/network-database',
    'how_peerselection':      'docs/how/peer-selection',
    'how_threatmodel':        'docs/how/threat-model',
    'how_tunnelrouting':      'docs/how/tunnel-routing',
    'htproxyports':           'about/browser-config',
    'i2cp':                   'docs/protocol/i2cp',
    'i2cp_spec':              'docs/spec/i2cp',
    'i2np':                   'docs/protocol/i2np',
    'i2np_spec':              'docs/spec/i2np',
    'i2pcontrol':             'docs/api/i2pcontrol',
    'i2ptunnel':              'docs/api/i2ptunnel',
    'i2ptunnel_migration':    'misc/i2ptunnel-migration',
    'i2ptunnel_services':     'misc/i2ptunnel-services',
    'impressum':              'impressum',
    'intro':                  'about/intro',
    'invisiblenet':           'misc/invisiblenet',
    'jbigi':                  'misc/jbigi',
    'jrandom-awol':           'misc/jrandom-awol',
    'license-agreements':     'get-involved/develop/license-agreements',
    'licenses':               'get-involved/develop/licenses',
    'links':                  'links',
    'manualwrapper':          'misc/manual-wrapper',
    'ministreaming':          'docs/api/ministreaming',
    'minwww':                 'misc/minwww',
    'monotone':               'get-involved/guides/monotone',
    'myi2p':                  'misc/myi2p',
    'naming':                 'docs/naming',
    'naming_discussion':      'docs/discussions/naming',
    'netdb_discussion':       'docs/discussions/netdb',
    'newdevelopers':          'get-involved/guides/new-developers',
    'newtranslators':         'get-involved/guides/new-translators',
    'ntcp':                   'docs/transport/ntcp',
    'ntcp_discussion':        'docs/discussions/ntcp',
    'othernetworks':          'comparison/other-networks',
    'performance-history':    'about/performance/history',
    'performance':            'about/performance/future',
    'plugin_spec':            'docs/spec/plugin',
    'plugins':                'docs/plugins',
    'ports':                  'docs/ports',
    'pressetext-0.7':         'misc/pressetext-0.7',
    'protocols':              'docs/protocol',
    'ratestats':              'misc/ratestats',
    'release-signing-key':    'get-involved/develop/release-signing-key',
    'roadmap':                'get-involved/roadmap',
    'sam':                    'docs/api/sam',
    'samv2':                  'docs/api/samv2',
    'samv3':                  'docs/api/samv3',
    'signedkeys':             'get-involved/develop/signed-keys',
    'socks':                  'docs/api/socks',
    'streaming':              'docs/api/streaming',
    'supported_applications': 'docs/applications/supported',
    'team':                   'about/team',
    'techintro':              'docs/how/tech-intro',
    'ticket1056':             'misc/ticket1056',
    'ticket919':              'misc/ticket919',
    'todo':                   'get-involved/todo',
    'transition-guide':       'misc/transition-guide',
    'transition-guide.txt':   'misc/transition-guide.txt',
    'transport':              'docs/transport',
    'tunnel-alt-creation':    'docs/spec/tunnel-creation',
    'tunnel-alt':             'docs/tunnels/implementation',
    'tunnel':                 'docs/tunnels/old-implementation',
    'tunnel_discussion':      'docs/discussions/tunnel',
    'tunnel_message_spec':    'docs/spec/tunnel-message',
    'udp':                    'docs/transport/ssu',
    'udp_spec':               'docs/spec/ssu',
    'unidirectional-tunnels': 'docs/tunnels/unidirectional',
    'updates':                'docs/spec/updates',
    'upgrade-0.6.1.30':       'misc/upgrade-0.6.1.30',
}

LEGACY_BLOG_POSTS_MAP={
    'statnotes0108':         {'date': (2008, 2, 1), 'title': 'status'},
    'summerofcode-2011':     {'date': (2011, 6, 6), 'title': 'Ipredator-SoC'},
    'summerofcode-2011-end': {'date': (2011, 9, 3), 'title': 'Ipredator-SoC-itoopie-released'},
}

LEGACY_RELEASES_MAP={
    '0.6.1.30': (2007, 10, 7),
    '0.6.1.31': (2008, 2, 10),
    '0.6.1.32': (2008, 3, 9),
    '0.6.1.33': (2008, 4, 26),
    '0.6.2':    (2008, 6, 7),
    '0.6.3':    (2008, 8, 26),
    '0.6.4':    (2008, 10, 6),
    '0.6.5':    (2008, 12, 1),
    '0.7':      (2009, 1, 25),
    '0.7.1':    (2009, 3, 29),
    '0.7.2':    (2009, 4, 19),
    '0.7.3':    (2009, 5, 18),
    '0.7.4':    (2009, 6, 13),
    '0.7.5':    (2009, 6, 29),
    '0.7.6':    (2009, 7, 31),
    '0.7.7':    (2009, 10, 12),
    '0.7.8':    (2009, 12, 8),
    '0.7.9':    (2010, 1, 12),
    '0.7.10':   (2010, 1, 22),
    '0.7.11':   (2010, 2, 15),
    '0.7.12':   (2010, 3, 15),
    '0.7.13':   (2010, 4, 27),
    '0.7.14':   (2010, 6, 7),
    '0.8':      (2010, 7, 12),
    '0.8.1':    (2010, 11, 15),
    '0.8.2':    (2010, 12, 22),
    '0.8.3':    (2011, 1, 24),
    '0.8.4':    (2011, 3, 2),
    '0.8.5':    (2011, 4, 18),
    '0.8.6':    (2011, 5, 16),
    '0.8.7':    (2011, 6, 27),
    '0.8.8':    (2011, 8, 23),
    '0.8.9':    (2011, 10, 11),
    '0.8.10':   (2011, 10, 20),
    '0.8.11':   (2011, 11, 8),
    '0.8.12':   (2012, 1, 6),
    '0.8.13':   (2012, 2, 27),
    '0.9':      (2012, 5, 2),
    '0.9.1':    (2012, 7, 30),
    '0.9.2':    (2012, 9, 21),
    '0.9.3':    (2012, 10, 27),
    '0.9.4':    (2012, 12, 17),
    '0.9.5':    (2013, 3, 8),
    '0.9.6':    (2013, 5, 28),
    '0.9.7':    (2013, 7, 15),
    '0.9.7.1':  (2013, 8, 10),
    '0.9.8':    (2013, 9, 30),
    '0.9.8.1':  (2013, 10, 2),
    '0.9.9':    (2013, 12, 7),
    '0.9.10':   (2014, 01, 22),
}

def legacy_show(f):
    lang = 'en'
    if hasattr(g, 'lang') and g.lang:
        lang = g.lang
    if lang == 'zh':
        lang = 'zh_CN'
    if f in SHORTCODES:
        return redirect(url_for(SHORTCODES[f]['function'], lang=lang, **SHORTCODES[f]['params']), 301)
    elif f in LEGACY_FUNCTIONS_MAP:
        return redirect(url_for(LEGACY_FUNCTIONS_MAP[f]['function'], lang=lang, **LEGACY_FUNCTIONS_MAP[f]['params']), 301)
    elif f in LEGACY_PAGES_MAP:
        return redirect(url_for('site_show', lang=lang, page=LEGACY_PAGES_MAP[f]), 301)
    elif f in LEGACY_BLOG_POSTS_MAP:
        return legacy_blog(lang, LEGACY_BLOG_POSTS_MAP[f]['date'], LEGACY_BLOG_POSTS_MAP[f]['title'])
    else:
        return redirect(url_for('site_show', lang=lang, page=f), 301)

def legacy_meeting(id):
    return redirect(url_for('meetings_show', id=id, lang='en'), 301)

def legacy_status(year, month, day):
    return legacy_blog('en', (year, month, day), 'status')

def legacy_release(version):
    lang = 'en'
    if hasattr(g, 'lang') and g.lang:
        lang = g.lang
    if version in LEGACY_RELEASES_MAP:
        return legacy_blog(lang, LEGACY_RELEASES_MAP[version], '%s-Release' % version)
    else:
        return legacy_show('release-%s' % version)

def legacy_blog(lang, (year, month, day), title):
    return redirect(url_for('blog_post', lang=lang, slug=('%d/%02d/%02d/%s' % (year, month, day, title))), 301)
