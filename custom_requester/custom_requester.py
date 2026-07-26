import json
import logging
import os
import requests
from utils.data import HEADERS  # <-- берем отсюда

class CustomRequester:
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url
        self.headers = HEADERS.copy()  # <-- из data.py
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.session.headers.update(self.headers)

    def send_request(self, method, endpoint, data=None, params=None, expected_status=200, need_logging=True):
        url = f"{self.base_url}{endpoint}"

        if endpoint in ["/login", "/register"]:
            self.session.headers.pop("Authorization", None)

        response = self.session.request(method, url, json=data, params=params)

        if need_logging:
            self.log_request_and_response(response)

        if response.status_code != expected_status:
            raise AssertionError(
                f"Unexpected status code: {response.status_code}. Expected: {expected_status}. "
                f"Response: {response.text}"
            )

        if endpoint == "/login" and response.status_code in [200, 201]:
            try:
                token = response.json().get("accessToken")
                if token:
                    self.update_session_headers(Authorization=f"Bearer {token}")
            except:
                pass

        return response

    def update_session_headers(self, **kwargs):
        self.headers.update(kwargs)
        self.session.headers.update(kwargs)

    def log_request_and_response(self, response):
        try:
            request = response.request
            GREEN = '\033[32m'
            RED = '\033[31m'
            RESET = '\033[0m'
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                body = f"-d '{body}' \n" if body and body != '{}' else ''

            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}")
            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_status = response.status_code
            is_success = response.ok
            response_data = response.text

            try:
                response_data = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                pass

            self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")
            color = GREEN if is_success else RED
            self.logger.info(
                f"\tSTATUS_CODE: {color}{response_status}{RESET}\n"
                f"\tDATA:\n{response_data}"
            )
            self.logger.info(f"{'=' * 80}\n")
        except Exception as e:
            self.logger.error(f"\nLogging failed: {type(e)} - {e}")