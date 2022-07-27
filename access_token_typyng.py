from datetime import datetime
from typing import Optional, NamedTuple


class AccessTokenResult(NamedTuple):
    access_token: Optional[str]
    expires_at: Optional[datetime]
    user_id: Optional[int]
