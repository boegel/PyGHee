# This file is part of PyGHee (pronounced as "piggy"), the GitHub Event Executor,
# is a GitHub App to process GitHub events, implemented in Python;
# see https://github.com/boegel/pyghee
#
# author: Kenneth Hoste (@boegel)
#
# license: GPLv2
#
import datetime
import flask
import hmac
import github
import json
import os
import traceback

from .utils import create_file, error, log, log_warning

EVENTS_LOG_DIR = os.path.join(os.getcwd(), 'events_log')
SHA1 = 'sha1'
UNKNOWN = 'UNKNOWN'


def get_event_info(request):
    """
    Extract event info from raw header data, and return result as Python dictionary value
    """
    event_info = {
        'action': request.json.get('action', UNKNOWN),
        'id': request.headers['X-Github-Delivery'],
        'signature-sha1': request.headers['X-Hub-Signature'],
        'timestamp_raw': request.headers['Timestamp'],
        'type': request.headers['X-GitHub-Event'],
    }

    event_info.update({
        'raw_request_body': request.json,
        'raw_request_data': request.data,
        'raw_request_headers': dict(request.headers),
    })

    timestamp = datetime.datetime.utcfromtimestamp(int(event_info['timestamp_raw'])/1000.)
    event_info['timestamp'] = timestamp
    event_info['date'] = timestamp.isoformat().split('T')[0]
    event_info['time'] = timestamp.isoformat().split('T')[1].split('.')[0].replace(':', '-')

    return event_info


class PyGHee(flask.Flask):

    def __init__(self, *args, **kwargs):
        """
        PyGHee constructor.
        """
        super(PyGHee, self).__init__('PyGHee', *args, **kwargs)

        github_token = os.getenv('GITHUB_TOKEN')
        if github_token is None:
            error("GitHub token is not available via $GITHUB_TOKEN!")
        else:
            del os.environ['GITHUB_TOKEN']

        self.gh = github.Github(github_token)

        # see https://docs.github.com/en/developers/webhooks-and-events/securing-your-webhooks
        self.github_app_secret_token = os.getenv('GITHUB_APP_SECRET_TOKEN')
        if self.github_app_secret_token is None:
            error("Webhook secret is not available via $GITHUB_APP_SECRET_TOKEN!")
        else:
            del os.environ['GITHUB_APP_SECRET_TOKEN']

    def handle_event(self, event_info, log_file=None):
        """
        Handle event
        """
        event_type = event_info['type']

        handler_method_name = 'handle_%s_event' % event_type
        handler = getattr(self, handler_method_name, None)

        if handler is None:
            msg = "[event id %(id)s] No handler found for event type '%(type)s' (action: %(action)s) - "
            msg += "event was received but left unhandled!"
            log_warning(msg % event_info, log_file=log_file)
        else:
            log("[event id %(id)s] Handler found for event type '%(type)s' (action: %(action)s)" % event_info)
            handler(event_info, log_file=log_file)

    def log_event(self, event_info, events_log_dir=None, log_file=None):
        """
        Log event data
        """
        if events_log_dir is None:
            events_log_dir = os.path.join(os.getcwd(), 'events_log')

        event_action = event_info['action']
        event_date = event_info['date']
        event_id = event_info['id']
        event_type = event_info['type']
        raw_request_body = event_info['raw_request_body']
        raw_request_headers = event_info['raw_request_headers']

        event_log_fn = '%sT%s_%s' % (event_date, event_info['time'], event_id)

        event_log_path = os.path.join(events_log_dir, event_type, event_action, event_date, event_log_fn)
        create_file(event_log_path + '_headers.json', json.dumps(raw_request_headers, sort_keys=True, indent=4))
        create_file(event_log_path + '_body.json', json.dumps(raw_request_body, sort_keys=True, indent=4))

        tup = (event_id, event_type, event_action, event_log_path)
        log("Event received (id: %s, type: %s, action: %s), event data logged at %s" % tup, log_file=log_file)

    def verify_request(self, event_info, abort_function, log_file=None):
        """
        Verify request by checking webhook secret in request header.
        Webhook secret must also be available in $GITHUB_APP_SECRET_TOKEN environment variable.
        """

        header_signature = event_info['signature-sha1']
        # if no signature is found, the request is forbidden
        if header_signature is None:
            log_warning("Missing signature in request header => 403", log_file=log_file)
            abort_function(403)
        else:
            header_parts = header_signature.split('=')
            if len(header_parts) == 2:
                signature_type, signature = header_parts
                if signature_type == SHA1:
                    # see https://docs.python.org/3/library/hmac.html
                    request_data = event_info['raw_request_data']
                    mac = hmac.new(self.github_app_secret_token.encode(), msg=request_data, digestmod=SHA1)
                    if hmac.compare_digest(str(mac.hexdigest()), str(signature)):
                        log("Request verified: signature OK!", log_file=log_file)
                    else:
                        log_warning("Faulty signature in request header => 403", log_file=log_file)
                        abort_function(403)
                else:
                    # we only know how to verify a SHA1 signature
                    log_warning("Uknown type of signature (%s) => 501" % signature_type, log_file=log_file)
                    abort_function(501)
            else:
                log_warning("Type of signature not specified (%s) => 501" % header_signature, log_file=log_file)
                abort_function(501)

    def process_event(self, request, abort_function,
                      events_log_dir=None, log_file=None, raise_error=False, verify=True):
        """
        Process a single event (log + verify + handle).
        Logs a warning in case of crash while processing event.
        """
        try:
            event_info = get_event_info(request)
            self.log_event(event_info, events_log_dir=events_log_dir, log_file=log_file)
            if verify:
                self.verify_request(event_info, abort_function, log_file=log_file)
            self.handle_event(event_info, log_file=log_file)
        except Exception as err:
            if raise_error:
                raise
            else:
                tb_txt = ''.join(traceback.format_exception(None, err, err.__traceback__))
                log_warning("A crash occurred!\n" + tb_txt, log_file=log_file)


def create_app(klass=None):
    """
    Create Flask app.
    """
    if klass is None:
        klass = PyGHee
    app = klass()

    @app.route('/', methods=['POST'])
    def main():
        app.process_event(flask.request, flask.abort)
        return ''

    return app
