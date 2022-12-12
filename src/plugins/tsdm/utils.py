import os
import json
from .config import tsdm_config
import requests
from requests.utils import dict_from_cookiejar
import privatebinapi
from requests.cookies import RequestsCookieJar
from nonebot.log import logger
from requests.utils import cookiejar_from_dict


def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def check_file(path, file_name):
    if os.path.exists(os.path.join(path, file_name)):
        return True
    else:
        return False


# save_file should only be used when you need to save as bytes.
def save_file(file_path, file_name, content):
    path = os.path.join(tsdm_config.tsdm_data_dir, file_path)
    check_path(path)
    with open(os.path.join(path, file_name), 'wb') as f:
        f.write(content)



def save_cookies(cookies: RequestsCookieJar):
    cookies_dict = dict_from_cookiejar(cookies)
    path = tsdm_config.tsdm_data_dir
    check_path(path)
    with open(os.path.join(path, 'cookies.json'), 'w') as f:
        f.write(json.dumps(cookies_dict))
    logger.info('Cookies saved.')


def load_cookies() -> RequestsCookieJar:
    path = tsdm_config.tsdm_data_dir
    if check_file(path, 'cookies.json'):
        with open(os.path.join(path, 'cookies.json'), 'r') as f:
            cookies_dict = json.loads(f.read())
        logger.info('Cookies loaded.')
        return cookiejar_from_dict(cookies_dict)
    else:
        logger.warning('Cookies file not found.')
        return RequestsCookieJar()


def pastebin_send(content: str) -> str:
    url = 'https://paste.to/'
    try:
        response = privatebinapi.send(url, text=content)
        logger.info(response)
        return response["full_url"]
    except Exception as e:
        logger.error('Pastebin send failed: {}'.format(e))
        return ''