import os

from dotenv import load_dotenv
from models import Kline
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib import parse

# Take environment variables from .env
load_dotenv()

db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT')
db_user = os.environ.get('DB_USER')
db_pass = parse.quote_plus(os.environ.get('DB_PASS'))
db_name = os.environ.get('DB_NAME')

db = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
engine = create_engine(db)

# Create a session variable. Allows all our transactions to be ran in the context of a session
Session = sessionmaker(bind = engine)

Base = declarative_base()

def create_table():
    # Create a new session
    session = Session()

    # Attempts to create the base tables and populate the db in a session.
    # In case of an issue rolls back the session
    try:
        # Generate schema
        Base.metadata.create_all(engine)
        session.commit()
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()

def save_klines(df):
    df.to_sql('klines_temp', engine, if_exists = 'replace', index = False)
    # https://www.programcreek.com/python/example/105995/sqlalchemy.dialects.postgresql.insert
    # from sqlalchemy.dialects.postgresql import insert
    # kline_table = Kline.__tablename__
    # ins = insert(kline_table)
    # upsert = ins.on_conflict_do_update(constraint = kline_table.primary_key, set_ = {
    #         'open': ins.excluded.open,
    #         'high': ins.excluded.high,
    #         'low': ins.excluded.low,
    #         'close': ins.excluded.close,
    #         'volume': ins.excluded.volume
    # })
    # with engine.begin() as conn:
    #     conn.execute(upsert, [dict(
    #         start_time = row[0],
    #         symbol = row[1],
    #         open = row[0],
    #         high = row[1],
    #         low = row[2],
    #         close = row[3],
    #         volume = row[4]) for row in rows])

    try:
        with engine.connect() as conn:
            conn.execute(text('''
                INSERT INTO klines (start_time, symbol, open, high, low , close, volume)
                SELECT * FROM klines_temp
                ON CONFLICT (start_time, symbol)
                DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume;
            '''))
            conn.execute(text('DROP TABLE klines_temp;'))
            conn.commit()
    except SQLAlchemyError as e:
        conn.rollback()
        print(str(e))
    finally:
        conn.close()
