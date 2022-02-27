# PyGHee

PyGHee (pronounced as "piggy") is the GitHub Event Executor, a Python library to facilitate creating a [GitHub App](https://docs.github.com/en/developers/apps) 
implemented in Python to process [events from GitHub](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads) (like the creation of a pull request, a comment being posted in an issue, etc.).

It takes care of:

* detailed logging of all event activity;
* logging all incoming events in JSON format;
* verifying incoming events to check whether they're indeed coming from GitHub (see also [Validating payloads from GitHub](https://docs.github.com/en/developers/webhooks-and-events/webhooks/securing-your-webhooks#validating-payloads-from-github));
* collecting event information in an easy to digest format to make processing of events easier;
* handling events by calling the appropriate `handle_*_event` method (if it is implemented);

## Requirements

`PyGHee` depends on a couple of Python libraries:

* [Flask](https://pypi.org/project/Flask), a simple framework for building complex web applications;
* [PyGithub](https://pypi.org/project/PyGithub), a Python library to access the [GitHub REST API](https://docs.github.com/en/rest);
* [waitress](https://pypi.org/project/waitress), a production-quality pure-Python [WSGI](https://www.python.org/dev/peps/pep-3333) server;

For more specific information, like required versions, see [requirements.txt](requirements.txt).

In addition:
* a [GitHub Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) must be available via the `$GITHUB_TOKEN` environment variable;
* the [GitHub app secret token](https://docs.github.com/en/developers/webhooks-and-events/webhooks/securing-your-webhooks) must be available via the `$GITHUB_APP_SECRET_TOKEN` environment variable;

## Installation

`PyGHee` is available on [PyPI](https://pypi.org/project/PyGHee/), so you can install it with `pip` (or another standard Python package installation tool):

```
pip3 install PyGHee
```

## Using PyGHee

To use `PyGHee`, you should implement a Python class that derives from the `PyGHee` class that is provided by the `pyghee.lib` module,
and implement one or more `handle_*_event` methods that correspond to the types of events you want to act on.

A list of event types is available in the [GitHub documentation](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads).

Each `handle_*_event` is passed a Python dictionary as first argument that contains event information.
The location of the `PyGHee` log file is specified as a second named argument `log_file`.

So if there would be an event type named `example`, the corresponding method should be implemented as:

```python
from pyghee.lib import PyGHee

class ExamplePyGHee(PyGHee):

    def handle_example_event(self, event_info, log_file=None):
        # implementation of handling example event goes here
```

If no `handle_*_event` method is implemented for a particular event type, a message is logged to signal this.
For example:
```
[20220227-T17:06:35] WARNING: [event id e81030bc-238d-440f-b438-54ba902a2224] No handler found for event type 'issue_comment' (action: created) - event was received but left unhandled!
```

Your main program should use the `create_app` function and serve it using [waitress](https://pypi.org/project/waitress):

```python
app = create_app(klass=ExamplePyGHee)
waitress.serve(app, listen='*:3000')
```

## Location of log file

The `PyGHee` log file is named `pyghee.log` is located in the directory where the GitHub App is started, and is only appended (not overwritten if it already existed).

## Location and structure of event logs

Event data is logged in JSON format in a directory named `events_log` that is located in the directory where the GitHub App is started.

The logs are organised hierarchically, by *event type*, *event action*, *date* (in that order).

For each incoming event, two JSON files are created, one for:
* the request headers including high-level information like the timestamp on which the event occured, etc.
* the request body including the actual event information (which depends on the event type).

Here's an example of a single event that got logged: an issue commented that was created on 20 Feb 2022 at 14:23:27:
```
$ ls events_log/issue_comment/created/2022-02-20/
2022-02-20T14-23-27_d3ed7694-8a6c-4008-a93f-b92aa86a95a8_body.json
2022-02-20T14-23-27_d3ed7694-8a6c-4008-a93f-b92aa86a95a8_headers.json
```

## Example

Here's an example of how to use `PyGHee`.

Copy-paste this into a file named `pyghee_example.py`:

```python
import waitress

from pyghee.lib import PyGHee, create_app
from pyghee.utils import log

class ExamplePyGHee(PyGHee):

    def handle_issue_comment_event(self, event_info, log_file=None):
        """
        Handle adding/removing of comment in issue or PR.
        """
        request_body = event_info['raw_request_body']
        issue_url = request_body['issue']['url']
        comment_author = request_body['comment']['user']['login']
        comment_txt = request_body['comment']['body']
        log("Comment posted in %s by @%s: %s" % (issue_url, comment_author, comment_txt))
        log("issue_comment event handled!", log_file=log_file)


if __name__ == '__main__':
    app = create_app(klass=ExamplePyGHee)
    log("App started!")
    waitress.serve(app, listen='*:3000')
```

To run your GitHub App:

* Define environment variables for [GitHub Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) and [GitHub app secret token](https://docs.github.com/en/developers/webhooks-and-events/securing-your-webhooks):
  ```
  export GITHUB_TOKEN=...
  export GITHUB_APP_SECRET_TOKEN=...
  ```

* Start your GitHub App:
  ```
  python3 -m pyghee_example
  ```

You should see a log file named `pyghee.log` that is created in the directory where your GitHub App was started from, which includes a message like:
```
[20220227-T18:54:49] App started!
```

## Test suite

To run the test suite, use [`pytest`](https://pypi.org/project/pytest):

```
pytest -v -s
```
