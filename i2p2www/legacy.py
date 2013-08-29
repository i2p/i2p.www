from flask import g, redirect, url_for


##############
# Legacy paths

LEGACY_FUNCTIONS_MAP={
    'announcements': {'function': 'blog_index',       'params': {}},
    'debian':        {'function': 'downloads_select', 'params': {'file': 'debian'}},
    'download':      {'function': 'downloads_list',   'params': {}},
    'statusnotes':   {'function': 'blog_index',       'params': {}},
}

LEGACY_PAGES_MAP={
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
    'contact':                'about/contact',
    'cvs':                    'misc/cvs',
    'datagrams':              'docs/api/datagrams',
    'dev-guidelines':         'get-involved/guides/dev-guidelines',
    'developerskeys':         'get-involved/develop/developers-keys',
    'donate':                 'get-involved/donate',
    'faq':                    'support/faq',
    'getinvolved':            'get-involved',
    'geoip':                  'docs/spec/geoip',
    'glossary':               'support/glossary',
    'halloffame':             'about/hall-of-fame',
    'how':                    'docs',
    'how_cryptography':       'docs/how/cryptography',
    'how_elgamalaes':         'docs/how/elgamal-aes',
    'how_garlicrouting':      'docs/how/garlic-routing',
    'how_intro':              'docs/how/intro',
    'how_networkcomparisons': 'about/comparison',
    'how_networkdatabase':    'docs/how/network-database',
    'how_peerselection':      'docs/how/peer-selection',
    'how_threatmodel':        'docs/how/threat-model',
    'how_tunnelrouting':      'docs/how/tunnel-routing',
    'htproxyports':           'support/browser-config',
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
    'othernetworks':          'about/comparison/other-networks',
    'papers':                 'research/papers',
    'performance-history':    'support/performance/history',
    'performance':            'support/performance/future',
    'plugin_spec':            'docs/spec/plugin',
    'plugins':                'docs/plugins',
    'ports':                  'docs/ports',
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

def legacy_show(f):
    lang = 'en'
    if hasattr(g, 'lang') and g.lang:
        lang = g.lang
    if f in LEGACY_FUNCTIONS_MAP:
        return redirect(url_for(LEGACY_FUNCTIONS_MAP[f]['function'], lang=lang, **LEGACY_FUNCTIONS_MAP[f]['params']))
    elif f in LEGACY_PAGES_MAP:
        return redirect(url_for('site_show', lang=lang, page=LEGACY_PAGES_MAP[f]))
    else:
        return redirect(url_for('site_show', lang=lang, page=f))

def legacy_meeting(id):
    return redirect(url_for('meetings_show', id=id, lang='en'))

def legacy_status(year, month, day):
    return redirect(url_for('blog_post', lang='en', slug=('%d/%02d/%02d/status' % (year, month, day))))
