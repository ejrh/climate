import sys
import httplib
import os.path
import zipfile

from defs import *

seen_files = set()

def already_exists(prefix, name):
    if os.path.exists(name):
        return True
    if name in seen_files:
        return True
    
    
    zipname = prefix + '.zip'
    try:
        zf = zipfile.ZipFile(zipname, 'r')
    except IOError:
        return False
    
    for fn in zf.namelist():
        seen_files.add(fn)
    zf.close()
    #print >>sys.stderr, 'Loaded %d names from %s' % (len(zf.namelist()), zipname)
    
    return name in seen_files

HOST = "climatemodels.uchicago.edu"
URL = "/cgi-bin/maps/extract_AR5_map.cgi?model=%(model)s&variable=%(var)s&year=%(year)s&month=0&avg=0&level=%(level)s&levname=%(levname)s"

conn = httplib.HTTPConnection(HOST)
conn.connect()

for var, levname, level, model in generate_datasets():
    prefix = PREFIX % locals()
    print >>sys.stderr, 'Prefix',prefix
    
    for year in YEARS:
        url = URL % locals()
        name = NAME % locals()
        if already_exists(prefix, name):
            #print >>sys.stderr, 'Already exists:', name
            continue
        conn.request('GET', url)
        resp = conn.getresponse()
        data = resp.read()
        if len(data) < 1000:
            print >>sys.stderr, 'Skipping %s as %s was only %d bytes' % (prefix, name, len(data))
            break
        f = open(name, 'wb')
        f.write(data)
        f.close()
        print name, url

conn.close()
