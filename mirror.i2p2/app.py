from flask import Flask, redirect, request, render_template, abort
from random import randint
from sys import argv
try:
    import json
except ImportError:
    import simplejson as json


# try to create an memcache client
if len(argv[3:]) > 0:
    try:
        try:
            from cmemcache import Client
        except ImportError:
            from memcache import Client
        client=Client(argv[3:])
    except ImportError:
        client=None

# create application
app=Flask(__name__)

# extract domain
domain=argv[1]

# extract port
port=int(argv[2])

def read_mirrors():
    file = open('mirrors', 'r')
    dat = file.read()
    file.close()
    lines=dat.split('\n')
    ret={}
    for line in lines:
        try:
            obj=json.loads(line)
        except ValueError:
            pass
        if 'protocol' not in obj:
            continue
        protocol=obj['protocol']
        if protocol not in ret:
            ret[protocol]=[]
        ret[protocol].append(obj)
    return ret


@app.route('/')
def index():
    return redirect('http://www.%s/download' % domain)

@app.route('/select/<path:f>')
def select(f):
    mirrors=read_mirrors()
    obj=[]
    for protocol in mirrors.keys():
        a={}
        a['name']=protocol.upper()
        a['mirrors']=mirrors[protocol]
        for mirror in a['mirrors']:
            mirror['url']=mirror['url'] % f
        obj.append(a)
    return render_template('select.html', mirrors=obj, file=f, domain=domain)

@app.route('/<protocol>/<path:f>')
def get(protocol, f):
    mirrors=read_mirrors()
    if not protocol in mirrors:
        abort(404)
    mirrors=mirrors[protocol]
    return redirect(mirrors[randint(0, len(mirrors) - 1)] % f)

@app.route('/<f>')
def old_get(f):
    return redirect('http://i2p.googlecode.com/files/%s' % f)

if __name__ == '__main__':
    app.run(port=port)
