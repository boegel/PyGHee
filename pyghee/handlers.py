# This file is part of PyGHee (pronounced as "piggy"), the GitHub Event Executor,
# is a GitHub App to process GitHub events, implemented in Python;
# see https://github.com/boegel/pyghee
#
# author: Kenneth Hoste (@boegel)
#
# license: GPLv2
#
from .utils import log


def handle_issue_comment(gh, request, log_file=None):
    """
    Handle adding/removing of comment in issue or PR.
    """
    log("issue_comment event handled!", log_file=log_file)
