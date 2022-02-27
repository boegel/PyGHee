#!/usr/bin/env python3
#
# PyGHee (pronounced as "piggy"), the GitHub Event Executor,
# is a GitHub App to process GitHub events, implemented in Python;
# see https://github.com/boegel/pyghee
#
# author: Kenneth Hoste (@boegel)
#
# license: GPLv2
#
import waitress

from .lib import PyGHee, create_app
from .utils import log


class ExamplePyGHee(PyGHee):

    def handle_create_event(self, request, log_file=None):
        """
        Handle create event (new branch, for example).
        """
        log("create event handled!", log_file=log_file)

    def handle_issue_comment_event(self, request, log_file=None):
        """
        Handle adding/removing of comment in issue or PR.
        """
        log("issue_comment event handled!", log_file=log_file)


if __name__ == '__main__':
    app = create_app(klass=ExamplePyGHee)
    log("App started!")
    waitress.serve(app, listen='*:3000')
