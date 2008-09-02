#!/usr/bin/env python
import os
from jinja import Environment, FileSystemLoader
#from codecs import open

env = Environment(loader=FileSystemLoader('pages'), trim_blocks=True, friendly_traceback=False)


def get_files(folder):
    for fn in os.listdir(folder):
        if fn.startswith('_'):
            continue
        fn = os.path.join(folder, fn)
        if os.path.isdir(fn):
            for item in get_files(fn):
                yield item
        else:
            yield fn

for filename in get_files('pages'):
    print filename
    filename = filename.split('/', 2)[1]
    t = env.get_template(filename)
    f = open(os.path.join('out', filename), 'w')
    f.write(t.render(static=True).encode('utf-8'))
    f.close()