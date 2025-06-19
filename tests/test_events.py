# This file is part of PyGHee (pronounced as "piggy"), the GitHub Event Executor,
# is a GitHub App to process GitHub events, implemented in Python;
# see https://github.com/boegel/pyghee
#
# author: Kenneth Hoste (@boegel)
#
# license: GPLv2
#
import copy
import json
import os
import re

from pyghee.lib import get_event_info, read_event_from_json
from pyghee.main import ExamplePyGHee
from requests.structures import CaseInsensitiveDict

from tests.event_data import REQUEST_ID_001, REQUEST_ID_002, TIMESTAMP_001
from tests.event_data import CREATE_BRANCH_REQUEST, ISSUE_COMMENT_CREATED_REQUEST

TEST_REQUESTS = (CREATE_BRANCH_REQUEST, ISSUE_COMMENT_CREATED_REQUEST)
REQUEST_IDS = (REQUEST_ID_001, REQUEST_ID_002)

TEST_SECRET_TOKEN = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'


def dummy_abort_function(abort_code):
    raise Exception("abort! (%s)" % abort_code)


def test_get_event_info():
    for idx, request in enumerate(TEST_REQUESTS):
        res = get_event_info(request)
        event_action = request.json.get('action', 'UNKNOWN')
        assert res['action'] == event_action
        assert res['id'] == REQUEST_IDS[idx]
        event_type = request.headers['X-GitHub-Event']
        assert res['type'] == event_type


def test_read_event_from_json(tmpdir):
    test_json = os.path.join(tmpdir, 'test.json')
    with open(test_json, 'w') as fp:
        event_data = {
            'headers': {
                'Timestamp': '1654898255373',
                'X-Github-Delivery': '5591ee40-e908-11ec-9119-f43ca5b71fc9',
                'X-Github-Event': 'pull_request',
                'X-Hub-Signature': 'sha1=6d13f2fbbf00f1bea70cbc26386b98adb6793dbd',
            },
            'json': {
                'action': 'opened',
            },
        }
        json.dump(event_data, fp)
    res = read_event_from_json(test_json)
    assert isinstance(res.headers, CaseInsensitiveDict)
    assert res.headers['x-github-event'] == 'pull_request'
    assert isinstance(res.json, dict)
    assert res.json['action'] == 'opened'


def test_process_event(tmpdir):

    events_log_dir = os.path.join(tmpdir, 'events_log_dir')
    log_file = os.path.join(tmpdir, 'pyghee.log')

    os.environ['GITHUB_TOKEN'] = 'fake_token'
    os.environ['GITHUB_APP_SECRET_TOKEN'] = 'fake_app_secret_token'
    pyghee = ExamplePyGHee()

    for idx, request in enumerate(TEST_REQUESTS):
        event_info = get_event_info(request)
        event_action, event_type = event_info['action'], event_info['type']

        pyghee.process_event(request, dummy_abort_function, events_log_dir=events_log_dir,
                             log_file=log_file, raise_error=True, verify=False)

        # check whether event data has been saved to events log dir
        event_data_dir = os.path.join(events_log_dir, event_type, event_action, '2022-02-20')
        assert os.path.isdir(event_data_dir)

        request_id = REQUEST_IDS[idx]
        header_fp = '2022-02-20T14-23-27_%s_headers.json' % request_id
        body_fp = '2022-02-20T14-23-27_%s_body.json' % request_id
        assert sorted(os.listdir(event_data_dir)) == [body_fp, header_fp]

        # verify saved event header
        expected_header = {
            'Timestamp': TIMESTAMP_001,
            'X-GitHub-Event': event_type,
            'X-Github-Delivery': request_id,
        }
        with open(os.path.join(event_data_dir, header_fp), 'r') as fp:
            header_data = json.load(fp)
            for key in expected_header:
                assert header_data[key] == expected_header[key]

        # verify saved event body
        expected_body = {
            'action': event_action,
        }
        with open(os.path.join(event_data_dir, body_fp), 'r') as fp:
            body_data = json.load(fp)
            for key in expected_body:
                if key == 'action' and expected_body[key] == 'UNKNOWN':
                    assert key not in body_data
                else:
                    assert body_data[key] == expected_body[key]

        # check whether handing of event got logged
        regex = re.compile(r'^\[[0-9]{8}-T[0-9]{2}:[0-9]{2}:[0-9]{2}\] %s event handled!' % event_type, re.M)
        with open(log_file, 'r') as fp:
            txt = fp.read()
            assert regex.search(txt)


def test_verify_request(tmpdir):
    """
    Test verification of request, using test secret app token and empty string as request data
    """
    log_file = os.path.join(tmpdir, 'pyghee.log')

    os.environ['GITHUB_TOKEN'] = 'fake_token'
    os.environ['GITHUB_APP_SECRET_TOKEN'] = TEST_SECRET_TOKEN

    pyghee = ExamplePyGHee()
    request = copy.deepcopy(ISSUE_COMMENT_CREATED_REQUEST)
    request.headers['X-Hub-Signature'] = 'sha1=1b96b55ff0ef92529c2ecb63a737a113d3b2979d'

    pyghee.verify_request(get_event_info(request), dummy_abort_function, log_file=log_file)
