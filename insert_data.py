# import pandas as pd

from base_sql import engine
from models import Kline
from sqlalchemy.dialects.postgresql import insert

def save_klines(df):
    # https://www.programcreek.com/python/example/105995/sqlalchemy.dialects.postgresql.insert
    records = df.to_dict(orient = 'records')

    kline_table = Kline.__table__
    ins = insert(kline_table)
    upsert = ins.on_conflict_do_update(constraint = kline_table.primary_key, set_ = {
        'open': ins.excluded.open,
        'high': ins.excluded.high,
        'low': ins.excluded.low,
        'close': ins.excluded.close,
        'volume': ins.excluded.volume
    })
    with engine.begin() as conn:
        conn.execute(upsert, [r for r in records])
