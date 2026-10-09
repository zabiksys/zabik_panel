from datetime import date, datetime

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm.attributes import InstrumentedAttribute


def date2key(date_: date) -> int:
    return date_.year * 10000 + date_.month * 100 + date_.day


def key2date(key: int | pd.Series | None) -> date | pd.Series | None:
    if key is None:
        return None
    elif type(key) is int:
        return date(key // 10000, key % 10000 // 100, key % 100)
    elif type(key) is InstrumentedAttribute:
        return func.make_date(key // 10000, key % 10000 // 100, key % 100)
    else:
        return pd.to_datetime(key, format='%Y%m%d')


def key2datetime(key: int | pd.Series) -> datetime | pd.Series:
    if type(key) is int:
        return datetime.strptime(str(key), '%Y%m%d')
    else:
        return pd.to_datetime(key, format='%Y%m%d')
