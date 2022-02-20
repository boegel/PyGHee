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
import flask
import waitress

from .events import init_github, process_event
from .utils import log


def create_app(gh):
    """
    Create Flask app.
    """
    app = flask.Flask('pyghee')

    @app.route('/', methods=['POST'])
    def main():
        process_event(flask.request, gh, flask.abort)
        return ''

    return app


if __name__ == '__main__':
    gh = init_github()
    app = create_app(gh)
    log("App started!")
    waitress.serve(app, listen='*:3000')
