# This file is part of PyGHee (pronounced as "piggy"), the GitHub Event Executor,
# is a GitHub App to process GitHub events, implemented in Python;
# see https://github.com/boegel/pyghee
#
# author: Kenneth Hoste (@boegel)
#
# license: GPLv2
#
import datetime
import hmac
import github
import os
import pprint

from .utils import create_file, error, log, warn

EVENTS_LOG_DIR = os.path.join(os.getcwd(), 'events_log')
GITHUB_APP_SECRET_TOKEN = None
SHA1 = 'sha1'


def init_github():
    """
    Initialize connection with GitHub
    """

    github_token = os.getenv('GITHUB_TOKEN')
    if github_token is None:
        error("GitHub token is not available via $GITHUB_TOKEN!")
    else:
        del os.environ['GITHUB_TOKEN']

    gh = github.Github(github_token)

    return gh


def handle_event(gh, request):
    """
    Handle event
    """
    event_id = request.headers['X-Request-Id']
    event_type = request.headers["X-GitHub-Event"]
    event_action = request.json['action']
    tup = (event_id, event_type, event_action)
    log("WARNING: event (id: %s, type: %s, action: %d) was received but left unhandled!" % tup)


def log_event(request):
    """
    Log event data
    """
    event_id = request.headers['X-Request-Id']
    event_ts_raw = request.headers['Timestamp']
    event_type = request.headers['X-GitHub-Event']
    event_action = request.json['action']

    event_ts = datetime.datetime.fromtimestamp(event_ts_raw/1000.)
    event_date = event_ts.isoformat().split('T')[0]
    event_time = event_ts.isoformat().split('T')[1].split('.')[0].split(':')[0]

    event_log_fn = '%s_%s' % (event_time, event_id)

    event_log_path = os.path.join(EVENTS_LOG_DIR, event_type, event_action, event_date, event_time, event_log_fn)
    create_file(event_log_path + '_headers.json', pprint.pformat(dict(request.headers)))
    create_file(event_log_path + '_body.json', pprint.pformat(request.json))

    tup = (event_id, event_type, event_action, event_log_path)
    log("Event received (id: %s, type: %s, action: %s), event data logged at %s" % tup)


def verify_request(request, abort_function):
    """
    Verify request by checking webhook secret in request header.
    Webhook secret must also be available in $GITHUB_APP_SECRET_TOKEN environment variable.
    """
    # see https://docs.github.com/en/developers/webhooks-and-events/securing-your-webhooks
    global GITHUB_APP_SECRET_TOKEN
    if GITHUB_APP_SECRET_TOKEN is None:
        GITHUB_APP_SECRET_TOKEN = os.getenv('GITHUB_APP_SECRET_TOKEN')
        if GITHUB_APP_SECRET_TOKEN is None:
            error("Webhook secret is not available via $GITHUB_APP_SECRET_TOKEN!")
        else:
            del os.environ['GITHUB_APP_SECRET_TOKEN']

    header_signature = request.headers.get('X-Hub-Signature')
    # if no signature is found, the request is forbidden
    if header_signature is None:
        log("Missing signature in request header => 403")
        abort_function(403)
    else:
        signature_type, signature = header_signature.split('=')
        if signature_type == SHA1:
            # see https://docs.python.org/3/library/hmac.html
            mac = hmac.new(GITHUB_APP_SECRET_TOKEN.encode(), msg=request.data, digestmod=SHA1)
            if hmac.compare_digest(str(mac.hexdigest()), str(signature)):
                log("Request verified: signature OK!")
            else:
                log("Faulty signature in request header => 403")
                abort_function(403)
        else:
            # we only know how to verify a SHA1 signature
            log("Uknown type of signature (%s) => 501" % signature_type)
            abort_function(501)
