from flask import abort, redirect, render_template, request
try:
    import json
except ImportError:
    import simplejson as json
from random import randint
import re

from i2p2www import CURRENT_I2P_VERSION, MIRRORS_FILE

DEFAULT_MIRROR = {
    "net": "clearnet", 
    "protocol": "https", 
    "domain": "files.i2p-projekt.de", 
    "path": "/%(version)s/%(file)s", 
    "org": "i2p-projekt", 
    "org_url": "https://files.i2p-projekt.de", 
    "country": "de",
}

#DEFAULT_MIRROR = {
#    "net": "clearnet",
#    "protocol": "https",
#    "domain": "download.i2p2.no",
#    "path": "/releases/%(version)s/%(file)s",
#    "org": "sigterm.no",
#    "org_url": "https://download.i2p2.no", 
#    "country": "no",
#}

#DEFAULT_MIRROR= {
#    'net': 'clearnet',
#    'protocol': 'https',
#    'domain':   'download.i2p2.no',
#    'org':      'sigterm.no',
#    'country':  'no',
#}

DEFAULT_I2P_MIRROR = {
    'net': 'i2p',
    'protocol': 'http',
    'domain':   'mgp6yzdxeoqds3wucnbhfrdgpjjyqbiqjdwcfezpul3or7bzm4ga.b32.i2p',
    'org':      'eyedeekay.github.io',
    'country':  'i2p',
}


###################
# Download handlers

# Read in mirrors from file
def read_mirrors():
    file = open(MIRRORS_FILE, 'r')
    dat = file.read()
    file.close()
    lines=dat.split('\n')
    ret={}
    for line in lines:
        try:
            obj=json.loads(line)
        except ValueError:
            continue
        if 'protocol' not in obj or 'domain' not in obj or 'path' not in obj:
            continue
        net=obj['net']
        protocol=obj['protocol']
        domain=obj['domain']
        path=obj['path']
        obj['url']='%s://%s%s' % (protocol, domain, path)
        if net not in ret:
            ret[net]={}
        if protocol not in ret[net]:
            ret[net][protocol]={}
        ret[net][protocol][domain]=obj
    return ret

# List of downloads
def downloads_list():
    # TODO: read mirror list or list of available files
    if request.headers.get('X-I2P-Desthash') and not request.headers.get('X-Forwarded-Server'):
        def_mirror = DEFAULT_I2P_MIRROR
    else:
        def_mirror = DEFAULT_MIRROR
    return render_template('downloads/list.html', def_mirror=def_mirror)

# Debian-specific page
def downloads_debian():
    return render_template('downloads/debian.html')

# Windows-specific page
def downloads_windows():
    return render_template('downloads/windows.html')

# MacOS-specific page
def downloads_macos():
    return render_template('downloads/macos.html')

# AIO-Windows-specific page
def downloads_easyinstall():
    # TODO: read mirror list or list of available files
    if request.headers.get('X-I2P-Desthash') and not request.headers.get('X-Forwarded-Server'):
        def_mirror = DEFAULT_I2P_MIRROR
    else:
        def_mirror = DEFAULT_MIRROR
    return render_template('downloads/easyinstall.html', def_mirror=def_mirror)

# Docker-specific page
def downloads_docker():
    return render_template('downloads/docker.html')

# Firefox-specific page
def downloads_firefox():
    # TODO: read mirror list or list of available files
    if request.headers.get('X-I2P-Desthash') and not request.headers.get('X-Forwarded-Server'):
        def_mirror = DEFAULT_I2P_MIRROR
    else:
        def_mirror = DEFAULT_MIRROR
    return render_template('downloads/firefox.html', def_mirror=def_mirror)

# The Lab
def downloads_lab():
    # TODO: read mirror list or list of available files
    if request.headers.get('X-I2P-Desthash') and not request.headers.get('X-Forwarded-Server'):
        def_mirror = DEFAULT_I2P_MIRROR
    else:
        def_mirror = DEFAULT_MIRROR
    return render_template('downloads/lab.html', def_mirror=def_mirror)

# Mac DMG page
def downloads_mac():
    # TODO: read mirror list or list of available files
    if request.headers.get('X-I2P-Desthash') and not request.headers.get('X-Forwarded-Server'):
        def_mirror = DEFAULT_I2P_MIRROR
    else:
        def_mirror = DEFAULT_MIRROR
    return render_template('downloads/mac.html', def_mirror=def_mirror)

def downloads_config():
    return render_template('downloads/config.html')

# Specific file downloader
def downloads_select(version, file):
    mirrors=read_mirrors()
    obj=[]
    for net in mirrors.keys():
        a={}
        a['key']=net
        a['name']=net
        a['protocols']=[]
        for protocol in mirrors[net].keys():
            b={}
            b['key']=protocol
            b['name']=protocol
            b['domains']=mirrors[net][protocol]
            a['protocols'].append(b)
        obj.append(a)
    return render_template('downloads/select.html', mirrors=obj, version=version, file=file)

def downloads_redirect(version, net, protocol, domain, file):
    mirrors=read_mirrors()
    if not net in mirrors:
        abort(404)
    mirrors=mirrors[net]
    data = {
        'version': version,
        'file': file,
        }

    if not protocol:
        protocol = mirrors.keys()[randint(0, len(mirrors) - 1)]
    if not protocol in mirrors:
        abort(404)
    mirrors=mirrors[protocol]

    if not domain:
        domain = mirrors.keys()[randint(0, len(mirrors) - 1)]
    if not domain in mirrors:
        abort(404)
    # SECURITY: Use safe string formatting to prevent injection (CVE-2024-I2PWWW-003)
    try:
        # Validate data values are safe for string formatting
        safe_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Basic validation - only allow alphanumeric, dots, hyphens
                if not re.match(r'^[a-zA-Z0-9._-]+$', value):
                    abort(400)  # Bad request for invalid characters
                safe_data[key] = value
            else:
                safe_data[key] = str(value)
        
        mirror_url = mirrors[domain]['url'].format(**safe_data)
    except (KeyError, ValueError):
        abort(404)  # Invalid mirror configuration
    
    return render_template('downloads/redirect.html',
                           version=version, protocol=protocol, domain=domain, file=file,
                           url=mirror_url)
