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
    """
    Print error message and exit
    """
    sys.stderr.write("ERROR: %s\n" % msg)
    sys.exit(1)


def log(msg, log_file=None):
    """
    Log message
    """
    if log_file is None:
        log_file = os.path.join(os.getcwd(), 'pyghee.log')

    with open(log_file, 'a') as fh:
        timestamp = datetime.datetime.now().strftime("%Y%m%d-T%H:%M:%S")
        fh.write('[' + timestamp + '] ' + msg + '\n')


def log_warning(msg, log_file=None):
    """
    Log warning message
    """
    log("WARNING: %s" % msg, log_file=log_file)


def warn(msg):
    """
    Print warning message
    """
    sys.stderr.write("WARNING: %s\n" % msg)
