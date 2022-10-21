# Originally from: https://github.com/hyugogirubato/Kamyroll-Python,
# heavily modified and reduced in scope.
import requests
import session
from typing import Sequence

class crunchyroll:
    def __init__(self):
        self.session = session.get()

    def logged_in(self) -> bool:
        return 'account_id' in self.session

    def login(self, username, password) -> None:
        """If there's a failure logging in, an exception will be raised."""
        req = requests.session()
        data = {
            'username': username,
            'password': password,
            'grant_type': 'password',
            'scope': 'offline_access',
        }
        req.headers.update(session.get_authorization(self.session, False))
        r = req.post('https://beta-api.crunchyroll.com/auth/v1/token', data=data).json()
        if err := session.check_error(r):
            raise BaseException("login (get token): " + err)

        access_token = r.get('access_token')
        refresh_token = r.get('refresh_token')
        token_type = r.get('token_type')
        authorization = {'Authorization': f'{token_type} {access_token}'}
        account_id = r.get('account_id')

        headers = session.get_headers()
        headers.update(authorization)
        req.headers = headers

        r = req.get('https://beta-api.crunchyroll.com/index/v2').json()
        if err := session.check_error(r):
            raise BaseException("login (get cms): " + err)

        cms = r.get('cms')
        json_token = self.session.get('token')
        json_token['refresh_token'] = refresh_token
        json_token['bucket'] = cms['bucket']
        json_token['policy'] = cms['policy']
        json_token['signature'] = cms['signature']
        json_token['key_pair_id'] = cms['key_pair_id']
        json_token['expires'] = cms['expires']
        self.session['token'] = json_token
        self.session['account_id'] = account_id

        session.save(self.session)

    def history(self, num_entries: int=100) -> Sequence[dict]:
        """Returns an array of the user's previously watched shows."""
        authorization = session.get_authorization(self.session, True)
        headers = session.get_headers()
        headers.update(authorization)
        req = requests.session()
        req.headers = headers
        params = {
            'locale': session.get_locale(self.session),
            'page_size': str(num_entries)
        }
        endpoint = f'https://beta.crunchyroll.com/content/v1/watch-history/{self.session["account_id"]}'
        r = req.get(endpoint, params=params)
        if not r.ok:
            raise BaseException(f"get history failure: {r.status_code} {r.reason}")
        j = r.json()
        if err := session.check_error(j)
            raise BaseException("crunchyroll.history: " + err)
        return j['items']

