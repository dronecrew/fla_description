#!/usr/bin/env python

from __future__ import print_function
import jinja2
import argparse
import os
import fnmatch
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    dirname = os.path.dirname(args.filename)
    basename = os.path.basename(args.filename)
    print('dirname', dirname)
    print('basename', basename)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(dirname))
    template = env.get_template(basename)
    d = {'np': np}
    result = template.render(d)
    filename_out = args.filename.replace('.jinja','')
    with open(filename_out, 'w') as f_out:
        print('{:s} -> {:s}'.format(args.filename, filename_out))
        f_out.write(result)


