import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pprint import pprint
from dotenv import load_dotenv
from urllib import parse

# Take environment variables from .env
load_dotenv()
# db = os.environ.get('DB')
db_host = os.environ.get('DB_HOST')
db_port = os.environ.get('DB_PORT')
db_user = os.environ.get('DB_USER')
db_pass = parse.quote_plus(os.environ.get('DB_PASS'))
db_name = os.environ.get('DB_NAME')

db = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

engine = create_engine(db)
# engine.connect()
# pprint(f'Connection successful! : {engine}')

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
        print(f'Connected & db populated')
    except Exception as e:
        session.rollback()
        print(e)
    finally:
        session.close()
