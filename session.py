# Originally from: https://github.com/hyugogirubato/Kamyroll-Python,
# heavily modified and reduced in scope.
import os
import json
import requests
from typing import Dict

SESSION_FILE = 'session.json'


def get() -> dict:
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    return { 'token': {
                 'token_type': 'Basic',
                 'access_token': 'aHJobzlxM2F3dnNrMjJ1LXRzNWE6cHROOURteXRBU2Z6QjZvbXVsSzh6cUxzYTczVE1TY1k='
             }
           }


def get_authorization(session, refresh: bool) -> Dict[str, str]:
    if refresh:
        req = requests.session()
        data = {
            'refresh_token': session['token'].get('refresh_token'),
            'grant_type': 'refresh_token',
            'scope': 'offline_access',
        }

        req.headers.update(get_authorization(session, False))
        r = req.post('https://beta-api.crunchyroll.com/auth/v1/token', data=data).json()
        if err := check_error(r):
            raise BaseException("get_authorization: " + err)

        access_token = r.get('access_token')
        refresh_token = r.get('refresh_token')
        token_type = r.get('token_type')
        json_token = session.get('token')
        json_token['refresh_token'] = refresh_token
        session['token'] = json_token
        save(session)
    else:
        token_type = session['token'].get('token_type')
        access_token = session['token'].get('access_token')
    return {'Authorization': f'{token_type} {access_token}'}


def check_error(json_request: Dict) -> str:
    """If an error is indicated in the JSON, return a string."""
    err = ''
    if 'error' in json_request:
        error_code = json_request['error']
        if error_code == 'invalid_grant':
            err = 'JSON Error: Invalid login information. code=invalid_grant'
        else:
            err = f'JSON Error message: code={error_code}'
    elif 'message' in json_request and 'code' in json_request:
        err = f'JSON Error message: code={json_request["code"]}, {json_request["message"]}.'
    return err


def get_headers() -> Dict[str, str]:
    return {
        'User-Agent': 'Crunchyroll/3.10.0 Android/6.0 okhttp/4.9.1',
        'Content-Type': 'application/x-www-form-urlencoded',
    }


def save(session) -> None:
    with open(SESSION_FILE, 'w', encoding='utf-8') as f:
        f.write(json.dumps(session, indent=4, sort_keys=False, ensure_ascii=False))


def get_locale(session) -> str:
    bucket = session.get('token').get('bucket')
    country_code = bucket.split('/')[1]
    items = [
        'en-US',
        'en-GB',
        'es-419',
        'es-ES',
        'pt-BR',
        'pt-PT',
        'fr-FR',
        'de-DE',
        'ar-SA',
        'it-IT',
        'ru-RU',
    ]
    locale = items[0]
    for item in items:
        country = item.split('-')[1].strip()
        if country_code == country:
            locale = item
            break
    return locale
