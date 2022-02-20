# This file is part of PyGHee (pronounced as "piggy"), the GitHub Event Executor,
# is a GitHub App to process GitHub events, implemented in Python;
# see https://github.com/boegel/pyghee
#
# author: Kenneth Hoste (@boegel)
#
# license: GPLv2
#
import datetime
import os
import sys

LOG = os.path.join(os.getcwd(), 'pyghee.log')


def create_file(path, txt):
    """
    Create file at specified path with specified contents.
    """
    parent_dir = os.path.dirname(path)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    with open(path, 'w') as fp:
        fp.write(txt)


def error(msg):
    """Print error message and exit."""
    sys.stderr.write("ERROR: %s\n" % msg)
    sys.exit(1)


def log(msg):
    """
    Log message
    """
    with open(LOG, 'a') as fh:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-T%H:%M:%S")
        fh.write('[' + timestamp + '] ' + msg + '\n')


def warn(msg):
    sys.stderr.write("WARNING: %s\n" % msg)
