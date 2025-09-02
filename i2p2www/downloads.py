from flask import abort, redirect, render_template, request, jsonify
try:
    import json
except ImportError:
    import simplejson as json
from random import randint
import re
import os.path

from i2p2www import CURRENT_I2P_VERSION, MIRRORS_FILE, TEMPLATE_DIR

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

# Extract hashes and filenames from macros file
def extract_hashes_from_macros():
    macros_path = os.path.join(TEMPLATE_DIR, 'downloads', 'macros')
    if not os.path.exists(macros_path):
        return {}
    
    with open(macros_path, 'r') as f:
        content = f.read()
    
    # Dictionary to store hash variable name to hash value mapping
    hashes = {}
    
    # Regex to extract hash variables
    hash_pattern = re.compile(r'{%\s*set\s+(\w+_hash)\s*=\s*[\'"]([a-fA-F0-9]+)[\'"]')
    
    for match in hash_pattern.finditer(content):
        var_name = match.group(1)
        hash_value = match.group(2)
        hashes[var_name] = hash_value
    
    # Now map hash variables to their corresponding file patterns
    hash_to_file = {}
    
    # Extract the filename patterns for each package type
    if 'i2pinstall_windows_hash' in hashes:
        hash_to_file['i2pinstall_windows_hash'] = {
            'hash': hashes['i2pinstall_windows_hash'],
            'filename_pattern': 'i2pinstall_{version}_windows.exe'
        }
    
    if 'i2pinstall_jar_hash' in hashes:
        hash_to_file['i2pinstall_jar_hash'] = {
            'hash': hashes['i2pinstall_jar_hash'], 
            'filename_pattern': 'i2pinstall_{version}.jar'
        }
    
    if 'i2psource_hash' in hashes:
        hash_to_file['i2psource_hash'] = {
            'hash': hashes['i2psource_hash'],
            'filename_pattern': 'i2psource_{version}.tar.bz2'
        }
    
    if 'i2pupdate_hash' in hashes:
        hash_to_file['i2pupdate_hash'] = {
            'hash': hashes['i2pupdate_hash'],
            'filename_pattern': 'i2pupdate_{version}.zip'
        }
    
    if 'i2p_android_hash' in hashes:
        hash_to_file['i2p_android_hash'] = {
            'hash': hashes['i2p_android_hash'],
            'filename_pattern': 'app.apk'
        }
    
    if 'i2p_macnative_hash' in hashes:
        # Extract the OSX launcher version from macros
        osx_version_pattern = re.compile(r'{%\s*set\s+i2p_macosx_launcher_version\s*=\s*[\'"]([^\'\"]+)[\'"]')
        osx_match = osx_version_pattern.search(content)
        osx_version = osx_match.group(1) if osx_match else '1.9.0'
        
        hash_to_file['i2p_macnative_hash'] = {
            'hash': hashes['i2p_macnative_hash'],
            'filename_pattern': 'I2PMacLauncher-{version}-beta-' + osx_version + '.dmg'
        }
    
    if 'i2p_bundle_hash' in hashes:
        hash_to_file['i2p_bundle_hash'] = {
            'hash': hashes['i2p_bundle_hash'],
            'filename_pattern': 'i2p-bundle-{version}.exe'
        }
    
    # Generate final JSON with actual filenames using current version
    result = {}
    for key, data in hash_to_file.items():
        filename = data['filename_pattern'].format(version=CURRENT_I2P_VERSION)
        result[filename] = data['hash']
    
    return result

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
    return render_template('downloads/redirect.html',
                           version=version, protocol=protocol, domain=domain, file=file,
                           url=mirrors[domain]['url'] % data)

# JSON endpoint for hashes
def downloads_hashes():
    """Return JSON with hashes and filenames from the macros file"""
    hashes = extract_hashes_from_macros()
    return jsonify(hashes)

