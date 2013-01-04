from flask import g, redirect, url_for


##############
# Legacy paths

LEGACY_FUNCTIONS_MAP={
    'announcements': 'blog_index',
    'download':      'downloads_list',
    'statusnotes':   'blog_index',
}

LEGACY_PAGES_MAP={
    'applications':           'volunteer/develop/applications',
    'benchmarks':             'misc/benchmarks',
    'bittorrent':             'docs/applications/bittorrent',
    'blockfile':              'docs/spec/blockfile',
    'bob':                    'docs/api/bob',
    'bounties':               'volunteer/bounties',
    'bounty_arabic':          'volunteer/bounties/arabic-trans',
    'bounty_btcclient':       'volunteer/bounties/btc-client',
    'bounty_datastore':       'volunteer/bounties/datastore',
    'bounty_debpack':         'volunteer/bounties/deb-pack',
    'bounty_i2phex':          'volunteer/bounties/i2phex',
    'bounty_ipv6':            'volunteer/bounties/ipv6',
    'bounty_rutrans':         'volunteer/bounties/russian-trans',
    'bounty_silc':            'volunteer/bounties/silc',
    'bounty_syndie2012':      'volunteer/bounties/syndie-2012',
    'bounty_unittests':       'volunteer/bounties/unit-tests',
    'bounty_vuzeplugin':      'volunteer/bounties/vuze-plugin',
    'clt':                    'misc/clt',
    'common_structures_spec': 'docs/spec/common-structures',
    'configuration':          'docs/spec/configuration',
    'contact':                'about/contact',
    'cvs':                    'misc/cvs',
    'datagrams':              'docs/spec/datagrams',
    'dev-guidelines':         'volunteer/guides/dev-guidelines',
    'developerskeys':         'volunteer/develop/developers-keys',
    'donate':                 'volunteer/donate',
    'faq':                    'support/faq',
    'getinvolved':            'volunteer',
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
    'license-agreements':     'volunteer/develop/license-agreements',
    'licenses':               'volunteer/develop/licenses',
    'links':                  'links',
    'manualwrapper':          'misc/manual-wrapper',
    'ministreaming':          'docs/api/ministreaming',
    'minwww':                 'misc/minwww',
    'monotone':               'volunteer/develop/monotone',
    'myi2p':                  'misc/myi2p',
    'naming':                 'docs/naming',
    'naming_discussion':      'docs/discussions/naming',
    'netdb_discussion':       'docs/discussions/netdb',
    'newdevelopers':          'volunteer/guides/new-developers',
    'newtranslators':         'volunteer/guides/new-translators',
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
    'release-signing-key':    'volunteer/develop/release-signing-key',
    'roadmap':                'volunteer/roadmap',
    'sam':                    'docs/api/sam',
    'samv2':                  'docs/api/samv2',
    'samv3':                  'docs/api/samv3',
    'signedkeys':             'volunteer/develop/signed-keys',
    'socks':                  'docs/api/socks',
    'streaming':              'docs/api/streaming',
    'supported_applications': 'docs/applications/supported',
    'team':                   'about/team',
    'techintro':              'docs/how/tech-intro',
    'todo':                   'volunteer/todo',
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
        return redirect(url_for(LEGACY_FUNCTIONS_MAP[f], lang=lang))
    elif f in LEGACY_PAGES_MAP:
        return redirect(url_for('site_show', lang=lang, page=LEGACY_PAGES_MAP[f]))
    else:
        return redirect(url_for('site_show', lang=lang, page=f))

def legacy_meeting(id):
    return redirect(url_for('meetings_show', id=id, lang='en'))

def legacy_status(year, month, day):
    return redirect(url_for('blog_entry', lang='en', slug=('%s/%s/%s/status' % (year, month, day))))
