import logging
import time

import requests

log = logging.getLogger("http")

USER_AGENT = "gies-program-health (contact: omvyas77@gmail.com)"
REQUEST_GAP_S = 0.5
TIMEOUT_S = 30
RETRIES = 3


def new_session():
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    return session


def fetch(session, url):
    failure = None
    for attempt in range(RETRIES + 1):
        time.sleep(REQUEST_GAP_S)
        try:
            response = session.get(url, timeout=TIMEOUT_S)
        except (requests.Timeout, requests.ConnectionError) as err:
            failure = repr(err)
        else:
            if response.status_code < 500:
                return response
            failure = f"HTTP {response.status_code}"
        if attempt < RETRIES:
            wait = 2 ** (attempt + 1)
            log.warning("%s failed (%s), retrying in %d s", url, failure, wait)
            time.sleep(wait)
    raise RuntimeError(f"{url} failed after {RETRIES + 1} attempts: {failure}")


def require_ok(response):
    # Anything but a 200 with a body fails the run, including the 202 with an empty body that
    # bot protection sends.
    assert response.status_code == 200 and response.content, (
        f"{response.url}: HTTP {response.status_code}, {len(response.content)} bytes"
    )
    return response.content
