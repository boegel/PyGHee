# This file is part of PyGHee (pronounced as "piggy"), the GitHub Event Executor,
# is a GitHub App to process GitHub events, implemented in Python;
# see https://github.com/boegel/pyghee
#
# author: Kenneth Hoste (@boegel)
#
# license: GPLv2
#
from collections import namedtuple

Request = namedtuple('Request', ['data', 'headers', 'json'])

ACTION_CREATED = 'created'

EVENT_TYPE_CREATE = 'create'
EVENT_TYPE_ISSUE_COMMENT = 'issue_comment'

REQUEST_ID_001 = 'd3ed7694-8a6c-4008-a93f-b92aa86a95a8'
TIMESTAMP_001 = '1645367007403'  # 2022-02-20T15:23:27

CREATE_BRANCH_REQUEST = Request(
    # request.data
    "".encode(),
    {
        # request.headers
        'Timestamp': TIMESTAMP_001,
        'X-GitHub-Event': EVENT_TYPE_CREATE,
        'X-Hub-Signature': 'sha1=0123456789abcedf0123456789abcedf01234567',  # fake signature!
        'X-Request-Id': REQUEST_ID_001,
    }, {
        # request.json
        'action': ACTION_CREATED,
    },
)

ISSUE_COMMENT_CREATED_REQUEST = Request(
    # request.data
    "".encode(),
    {
        # request.headers
        'Timestamp': TIMESTAMP_001,
        'X-GitHub-Event': EVENT_TYPE_ISSUE_COMMENT,
        'X-Hub-Signature': 'sha1=0123456789abcedf0123456789abcedf01234567',  # fake signature!
        'X-Request-Id': REQUEST_ID_001,
    }, {
        # request.json
        'action': ACTION_CREATED,
        'comment': {
            'body': "This is just a test",
            'user': {
                'login': 'boegel',
            },
        },
        'issue': {
            'url': 'https://github.com/boegel/PyGHee/issues/123456789',
        },
    },
)
