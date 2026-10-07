#!/usr/bin/env python3
"""Exercise the deployed frontend proxy and real API without extra dependencies.

Use only against a disposable classroom/CI deployment. Creates and removes one task.
"""
import json
import sys
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def main():
    base = sys.argv[1].rstrip('/')
    if urlparse(base).hostname not in {'localhost', '127.0.0.1'}:
        raise SystemExit('Use a localhost port-forward to the disposable deployment')

    def request(path, method='GET', body=None, expected=200):
        data = None if body is None else json.dumps(body).encode()
        req = Request(base + path, data=data, method=method,
                      headers={'Content-Type': 'application/json'})
        try:
            with urlopen(req, timeout=10) as response:
                status, content = response.status, response.read()
        except HTTPError as error:
            status, content = error.code, error.read()
        if status != expected:
            raise AssertionError(f'{method} {path}: expected {expected}, got {status}')
        return content

    deadline = time.monotonic() + 90
    while True:
        try:
            request('/ready')
            break
        except (URLError, AssertionError, TimeoutError):
            if time.monotonic() >= deadline:
                raise
            time.sleep(1)
    assert b'TaskBoard' in request('/'), 'Frontend HTML is missing TaskBoard'
    assert json.loads(request('/health'))['status'] == 'alive'
    assert b'taskboard_http_requests_total' in request('/metrics')
    print('PASS: frontend HTML, proxy, liveness, database readiness and metrics')

    body = {'title': f'CI deployment check {uuid.uuid4().hex[:12]}',
            'description': 'Disposable end-to-end validation', 'priority': 'high', 'status': 'todo'}
    created = json.loads(request('/api/tasks', 'POST', body, 201))
    path = f'/api/tasks/{created["id"]}'
    try:
        assert json.loads(request(path))['title'] == body['title']
        assert any(task['id'] == created['id'] for task in json.loads(request('/api/tasks')))
        body['status'] = 'done'
        assert json.loads(request(path, 'PUT', body))['status'] == 'done'
        assert json.loads(request('/api/tasks/stats'))['done'] >= 1
        request('/api/tasks', 'POST', {'title': 'invalid', 'status': 'invalid'}, 422)
        print('PASS: create, list, read, update, statistics and invalid-input rejection')
    finally:
        request(path, 'DELETE', expected=204)
    request(path, expected=404)
    print('PASS: delete and missing-task response; temporary task removed')


if __name__ == '__main__':
    main()
