import logging
import socket
import threading
import time
from urllib.parse import unquote_plus

import httpx
import pytest
import uvicorn

from app.main import app

FAKE_NAME = "Zzyzx Fakename"
FAKE_PHONE = "0999123456"


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.lines: list[str] = []

    def emit(self, record):
        self.lines.append(record.getMessage())


@pytest.fixture
def access_log(client):
    """Run the real app under uvicorn and capture what its access log writes."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 5
    while not server.started and time.time() < deadline:
        time.sleep(0.01)
    assert server.started, "uvicorn did not start"
    capture = _Capture()
    logging.getLogger("uvicorn.access").addHandler(capture)
    capture.base_url = f"http://127.0.0.1:{port}"
    yield capture
    logging.getLogger("uvicorn.access").removeHandler(capture)
    server.should_exit = True
    thread.join(timeout=5)


@pytest.mark.parametrize("term", [FAKE_NAME, FAKE_PHONE])
def test_search_term_is_not_written_to_access_log(access_log, term):
    # Same request the UI sends (frontend/src/api.ts listPatients).
    res = httpx.post(f"{access_log.base_url}/patients/search", json={"q": term})
    assert res.status_code == 200
    assert any(
        '"POST /patients/search' in line and line.endswith("200") for line in access_log.lines
    )
    leaked = [line for line in access_log.lines if term in unquote_plus(line)]
    assert leaked == []
