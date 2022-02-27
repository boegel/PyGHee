from collections import namedtuple

Request = namedtuple('Request', ['data', 'headers', 'json'])

ACTION_CREATED = 'created'

EVENT_TYPE_CREATE = 'create'
EVENT_TYPE_ISSUE_COMMENT = 'issue_comment'

REQUEST_ID_001 = 'd3ed7694-8a6c-4008-a93f-b92aa86a95a8'
TIMESTAMP_001 = '1645367007403'  # 2022-02-20T15:23:27

CREATE_BRANCH_REQUEST = Request("".encode(),
{
    'Timestamp': TIMESTAMP_001,
    'X-GitHub-Event': EVENT_TYPE_CREATE,
    'X-Request-Id': REQUEST_ID_001,
    'X-Hub-Signature': 'sha1=0123456789abcedf0123456789abcedf01234567',  # fake signature!
}, {
})

ISSUE_COMMENT_CREATED_REQUEST = Request("".encode(),
{
    'Timestamp': TIMESTAMP_001,
    'X-GitHub-Event': EVENT_TYPE_ISSUE_COMMENT,
    'X-Request-Id': REQUEST_ID_001,
    'X-Hub-Signature': 'sha1=0123456789abcedf0123456789abcedf01234567',  # fake signature!
}, {
    'action': ACTION_CREATED,
})
