import os
import sys
from typing import Optional

import requests

PUSHCUTS_URL = os.environ.get("PUSHCUTS_URL")


class PushcutsError(Exception):
    pass


def pushcut(title: str, text: str, pushcuts_url: Optional[str] = None):
    """
    Setting pushcuts_url overrides the value from environment variable
    """
    if pushcuts_url is None:
        if PUSHCUTS_URL is None:
            raise PushcutsError("Setting a pushcuts URL is required for notification")
        else:
            url = PUSHCUTS_URL
    else:
        url = pushcuts_url
    requests.get(url, {"title": title, "text": text})


def stdin_input():
    for line in sys.stdin:
        return line.strip()


def pushcuts_main(title: Optional[str] = None, text: Optional[str] = None):
    if title is not None and text is not None:
        pushcut(title, text)
    elif title is None and text is not None:
        pushcut(stdin_input(), text)
    elif title is not None and text is None:
        pushcut(title, stdin_input())
    else:
        pushcut("Terminal Notification", stdin_input())
