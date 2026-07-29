import json
import logging
import os

import requests
from pydantic import BaseModel

from constants.constants import RED, GREEN, RESET
from utils.data import HEADERS


class CustomRequester:
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url
        self.base_headers = HEADERS.copy()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # по ТЗ
        self.session.headers = self.base_headers.copy()

    def send_request(self, method, endpoint, data=None, params=None, expected_status=200, need_logging=True):
        url = f"{self.base_url}{endpoint}"

        if endpoint.endswith("/login") or endpoint.endswith("/register"):
            self.session.headers.pop("Authorization", None)

        # по ТЗ: если пришел Pydantic - переводим в json
        if isinstance(data, BaseModel):
            data = json.loads(data.model_dump_json(exclude_unset=True))

        response = self.session.request(method, url, json=data, params=params)

        if need_logging:
            self.log_request_and_response(response)

        if response.status_code != expected_status:
            raise AssertionError(
                f"Unexpected status code: {response.status_code}. Expected: {expected_status}. "
                f"Response: {response.text}"
            )

        if endpoint.endswith("/login") and response.status_code in [200, 201]:
            try:
                token = response.json().get("accessToken")
                if token:
                    self.update_session_headers(Authorization=f"Bearer {token}")
            except:
                pass

        return response

    def update_session_headers(self, **kwargs):
        self.base_headers.update(kwargs)
        self.session.headers.update(kwargs)

    def log_request_and_response(self, response):
        """
        Логгирование запросов и ответов. Настройки логгирования описаны в pytest.ini
        Преобразует вывод в curl-like (-H хэдэеры), (-d тело)

        :param response: Объект response получаемый из метода "send_request"
        """
        try:
            request = response.request
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                elif isinstance(request.body, str):
                    body = request.body
                body = f"-d '{body}' \n" if body != '{}' else ''

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
            except:
                pass

            if not is_success:
                self.logger.info(f"\tRESPONSE:"
                                 f"\nSTATUS_CODE: {RED}{response_status}{RESET}"
                                 f"\nDATA: {RED}{response_data}{RESET}")
            else:
                self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")
                self.logger.info(
                    f"\tSTATUS_CODE: {GREEN}{response_status}{RESET}\n"
                    f"\tDATA:\n{response_data}"
                )

        except Exception as e:
            self.logger.info(f"\nLogging went wrong: {type(e)} - {e}")