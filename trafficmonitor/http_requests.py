from pathlib import Path
import requests
from urllib3 import disable_warnings
import urllib.request
import logging

from trafficmonitor.helper_functions import create_path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

log_path = str(Path(f"{create_path()}/requests.log"))
file_handler = logging.FileHandler(log_path)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


PROXY = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}


def static_http_requests(**data):
    disable_warnings()
    method = data['method']
    url = data['url']
    header = data['header']
    content = data['content']
    timeout = data['timeout']
    num_of_retries = data['num_of_retries']

    system_proxy = urllib.request.getproxies()
    if len(system_proxy) > 0:
        proxies = system_proxy
    else:
        proxies = None

    try:
        req = requests.request(
            method, url, headers=header, data=content, verify=False,
            timeout=timeout, allow_redirects=False, proxies=proxies
        )
        return req.status_code, req.headers, req.text

    except requests.exceptions.RequestException:
        rsp = None
        for count in range(int(num_of_retries)):
            try:
                rsp = requests.request(
                    method, url, headers=header, data=content,
                    verify=False, timeout=timeout, allow_redirects=False, proxies=proxies
                )
            except requests.exceptions.RequestException as e:
                logger.exception(f"Not able to retry request {e}")

            if rsp is not None:
                break

        if rsp is None:
            return 'No Response', '', ''
