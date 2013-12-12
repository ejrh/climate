import sys
import os
import zipfile

from defs import *

def main():
    for var, levname, level, model in generate_datasets():
        prefix = PREFIX % locals()
        
        filenames = os.listdir('.')
        filenames = [fn for fn in filenames if fn.startswith(prefix) and not fn.endswith('.zip')]
        
        if len(filenames) == 0:
            continue
        
        zipname = prefix + '.zip'
        zf = zipfile.ZipFile(zipname, 'a', zipfile.ZIP_DEFLATED)
        for fn in filenames:
            zf.write(fn)
        zf.close()
        
        print zipname, len(filenames)

if __name__ == '__main__':
    main()
