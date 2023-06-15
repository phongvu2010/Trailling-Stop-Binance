import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pprint import pprint
from dotenv import load_dotenv

# Take environment variables from .env
load_dotenv()
db = os.environ.get('DB')

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
