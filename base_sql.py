import os
import pandas as pd

from dotenv import load_dotenv
from models import Base, Kline, Order
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from urllib import parse

try:
    # Take environment variables from .env
    load_dotenv()
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    db_user = os.environ.get('DB_USER')
    db_pass = parse.quote_plus(os.environ.get('DB_PASS'))
    db_name = os.environ.get('DB_NAME')

    db = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

    engine = create_engine(db)
    # engine.connect()

    # Create a session variable. Allows all our transactions to be ran in the context of a session
    Session = sessionmaker(bind = engine)
    session = Session()

    # This functions creates the table if it does not exist
    Base.metadata.create_all(engine)
except Exception as e:
    print(str(e))
    engine = None

def save_klines(df, symbol):
    # https://www.programcreek.com/python/example/105995/sqlalchemy.dialects.postgresql.insert
    df['symbol'] = symbol
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

def get_orders():
    try:
        tbl_name = Order.__tablename__
        return pd.read_sql_table(tbl_name, engine)
    except SQLAlchemyError as e:
        print('Unable to select records ' + print(str(e)))
        return None

def save_orders(df):
    records = df.to_dict(orient = 'records')

    order_table = Order.__table__
    ins = insert(order_table)
    upsert = ins.on_conflict_do_update(constraint = order_table.primary_key, set_ = {
        'time_order': ins.excluded.time_order,
        'type': ins.excluded.type,
        'act_price': ins.excluded.act_price,
        'limit_price': ins.excluded.limit_price,
        'delta': ins.excluded.delta
    })
    with engine.begin() as conn:
        conn.execute(upsert, [r for r in records])

# def save_klines(df):
#     df.to_sql('klines_temp', engine, if_exists = 'replace', index = False)

#     try:
#         with engine.connect() as conn:
#             conn.execute(text('''
#                 INSERT INTO klines (start_time, symbol, open, high, low , close, volume)
#                 SELECT * FROM klines_temp
#                 ON CONFLICT (start_time, symbol)
#                 DO UPDATE SET
#                 open = EXCLUDED.open,
#                 high = EXCLUDED.high,
#                 low = EXCLUDED.low,
#                 close = EXCLUDED.close,
#                 volume = EXCLUDED.volume;
#             '''))
#             conn.execute(text('DROP TABLE klines_temp;'))
#             conn.commit()
#     except SQLAlchemyError as e:
#         conn.rollback()
#         print(str(e))
#     finally:
#         conn.close()