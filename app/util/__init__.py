import datetime
import hashlib
import os
from html.parser import HTMLParser
from io import StringIO
from typing import Optional, Union
from uuid import uuid1

import pytz
from ..conf import settings

__HTML5Stripper__: Optional[type] = None


def the_now() -> datetime.datetime:
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


def the_ts_now() -> int:
    return the_now().timestamp()


def date_tz_or_diff(
    date: datetime.datetime,
    tzmindiff: Optional[int] = None,
    tz: Optional[str] = None
) -> datetime.datetime:
    if tzmindiff and tz:
        raise ValueError('Is either `tz` or `tzmindiff`.')

    if tzmindiff:
        return date + datetime.timedelta(minutes=tzmindiff)
    else:
        if not tz:
            tz = 'UTC'

        tz_object = pytz.timezone(tz)
        if not tz_object:
            raise ValueError("Unrecognized timezone %s" % tz)

        if date.tzinfo.zone == tz_object.zone:
            return date

        return date.astimezone(tz_object)


def hash_passwd(passwd: Union[str, bytes]):
    if not isinstance(passwd, bytes):
        passwd = passwd.encode()

    return hashlib.pbkdf2_hmac(
        "sha256", passwd,
        settings.app_secret_key, 512
    ).hex()


def strip_tags(html):
    global __HTML5Stripper__

    if __HTML5Stripper__ is None:
        class HTML5Stripper(HTMLParser):
            def __init__(self):
                super().__init__()
                self.reset()
                self.strict = False
                self.convert_charrefs = True
                self.text = StringIO()

            def handle_data(self, d):
                self.text.write(d)

            def get_data(self):
                return self.text.getvalue()

        __HTML5Stripper__ = HTML5Stripper
    
    s = __HTML5Stripper__()
    s.feed(html)
    return s.get_data()


def project_root_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def password_change_request_expiracy() -> datetime:
    return (
        datetime.datetime.utcnow().astimezone(tz=pytz.utc)
        + datetime.timedelta(minutes=settings.user_password_request_expires)
    )


def password_request_key() -> str:
    return hashlib.sha512(uuid1().hex.encode() + os.urandom(128)).hexdigest()
