import json
import github
import os
import re

from pyghee.events import get_basic_event_info, process_event

from tests.event_data import ACTION_CREATED, EVENT_TYPE_ISSUE_COMMENT, REQUEST_ID_001, TIMESTAMP_001
from tests.event_data import CREATE_BRANCH_EVENT, ISSUE_COMMENT_CREATED_EVENT

EVENT_DATA = (CREATE_BRANCH_EVENT, ISSUE_COMMENT_CREATED_EVENT)


def dummy_abort_function(_):
    raise Exception("abort!")


def test_get_basic_event_info():
    for event_data in EVENT_DATA:
        event_type = event_data.headers['X-GitHub-Event']
        event_action = event_data.json.get('action', 'UNKNOWN')
        expected = (REQUEST_ID_001, event_type, event_action)
        assert get_basic_event_info(event_data) == expected


def test_process_event(tmpdir):

    events_log_dir = os.path.join(tmpdir, 'events_log_dir')
    log_file = os.path.join(tmpdir, 'pyghee.log')

    gh = github.Github()

    for event_data in EVENT_DATA:
        event_type = event_data.headers['X-GitHub-Event']
        event_action = event_data.json.get('action', 'UNKNOWN')

        process_event(event_data, gh, dummy_abort_function, events_log_dir=events_log_dir,
                      log_file=log_file, raise_error=True, verify=False)

        # check whether event data has been saved to events log dir
        event_data_dir = os.path.join(events_log_dir, event_type, event_action, '2022-02-20')
        assert os.path.isdir(event_data_dir)

        header_fp = '2022-02-20T14-23-27_%s_headers.json' % REQUEST_ID_001
        body_fp = '2022-02-20T14-23-27_%s_body.json' % REQUEST_ID_001
        assert sorted(os.listdir(event_data_dir)) == [body_fp, header_fp]

        # verify saved event header
        expected_header = {
            'Timestamp': TIMESTAMP_001,
            'X-GitHub-Event': event_type,
            'X-Request-Id': REQUEST_ID_001,
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
