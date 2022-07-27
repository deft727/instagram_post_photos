import requests
import json
from typing import Optional
from datetime import timedelta

from django.utils import timezone
from django.conf import settings

from .access_token_typyng import AccessTokenResult


def get_long_lived_token(access_token: str) -> Optional[dict]:
    long_lived_token = requests.get(f" https://graph.instagram.com/access_token?grant_type="
                                    f"ig_exchange_token&client_secret={settings.INSTAGRAM_SECRET}&access_token="
                                    f"{access_token}")

    token = json.loads(long_lived_token.text).get('access_token')
    if token:
        new_token = requests.get(
            f'https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&&access_token={token}')
        token = json.loads(new_token.text)
        expires_at = timezone.now() + timedelta(seconds=token.get('expires_in'))
        if token.get('access_token'):
            return {'access_token': token.get('access_token'), 'expires_at': expires_at}


def get_token_and_user_id(code: str) -> AccessTokenResult:

    r = requests.post(settings.INSTAGRAM_ACCESS_TOKEN_URL, data={
        'app_id': settings.INSTAGRAM_APP_ID,
        'app_secret': settings.INSTAGRAM_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.INSTAGRAM_REDIRECT_URL,
        'code': code
    })

    if r.status_code == 200:
        response = json.loads(r.text)
        short_token = response['access_token']
        # get_username = requests.get(f'{settings.INSTAGRAM_USERNAME_LINK}={short_token}')
        token_with_data = get_long_lived_token(short_token)
        user_id = response['user_id']

        return AccessTokenResult(
            access_token=token_with_data.get('access_token'),
            expires_at=token_with_data.get('expires_at'),
            user_id=user_id,
        )
    else:
        raise ValueError(f'{r.text}')


def get_auth_url() -> str:
    return f'{settings.INSTAGRAM_AUTH_URL}?client_id={settings.INSTAGRAM_APP_ID}&redirect_uri=' \
           f'{settings.INSTAGRAM_REDIRECT_URL}&scope=user_profile,user_media&' \
           f'response_type=code&state=DyKeIHNbjTta&scope=user_profile'


def parse_response_code(code: str) -> Optional[str]:
    try:
        response = code.split('=')[1]
        code = response.split('&')[0]
        return code
    except AttributeError:
        return None
