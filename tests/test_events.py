import json
import github
import os
import re
from collections import namedtuple

from pyghee.events import get_basic_event_info, process_event


Request = namedtuple('Request', ['headers', 'json'])


def dummy_abort_function(_):
    raise Exception("abort!")


ACTION_CREATED = 'created'

EVENT_TYPE_ISSUE_COMMENT = 'issue_comment'

REQUEST_ID_001 = 'd3ed7694-8a6c-4008-a93f-b92aa86a95a8'

TIMESTAMP_001 = '1645367007403'  # 2022-02-20T15:23:27

ISSUE_COMMENT_CREATED_EVENT = Request({
    'Timestamp': TIMESTAMP_001,
    'X-GitHub-Event': EVENT_TYPE_ISSUE_COMMENT,
    'X-Request-Id': REQUEST_ID_001,
}, {
    'action': ACTION_CREATED,
})


def test_get_basic_event_info():
    expected = (REQUEST_ID_001, EVENT_TYPE_ISSUE_COMMENT, ACTION_CREATED)
    assert get_basic_event_info(ISSUE_COMMENT_CREATED_EVENT) == expected


def test_process_event(tmpdir):

    events_log_dir = os.path.join(tmpdir, 'events_log_dir')
    log_file = os.path.join(tmpdir, 'pyghee.log')

    gh = github.Github()
    process_event(ISSUE_COMMENT_CREATED_EVENT, gh, dummy_abort_function, events_log_dir=events_log_dir,
                  log_file=log_file, raise_error=True, verify=False)

    # check whether event data has been saved to events log dir
    event_data_dir = os.path.join(events_log_dir, 'issue_comment', 'created', '2022-02-20')
    assert os.path.isdir(event_data_dir)

    header_fp = '2022-02-20T15-23-27_%s_headers.json' % REQUEST_ID_001
    body_fp = '2022-02-20T15-23-27_%s_body.json' % REQUEST_ID_001
    assert sorted(os.listdir(event_data_dir)) == [body_fp, header_fp]

    # verify saved event header
    expected_header = {
        'Timestamp': TIMESTAMP_001,
        'X-GitHub-Event': EVENT_TYPE_ISSUE_COMMENT,
        'X-Request-Id': REQUEST_ID_001,
    }
    with open(os.path.join(event_data_dir, header_fp), 'r') as fp:
        header_data = json.load(fp)
        for key in expected_header:
            assert header_data[key] == expected_header[key]

    # verify saved event body
    expected_body = {
        'action': 'created',
    }
    with open(os.path.join(event_data_dir, body_fp), 'r') as fp:
        body_data = json.load(fp)
        for key in expected_body:
            assert body_data[key] == expected_body[key]

    # check whether handing of event got logged
    regex = re.compile(r'^\[[0-9]{8}-T[0-9]{2}:[0-9]{2}:[0-9]{2}\] issue_comment event handled!', re.M)
    with open(log_file, 'r') as fp:
        txt = fp.read()
        assert regex.search(txt)
