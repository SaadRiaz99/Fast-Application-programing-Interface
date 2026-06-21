from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from urllib.parse import quote_plus

password = quote_plus("24022007@")
DATABASE_URL = f"mysql+pymysql://root:{password}@localhost:3306/Printing"

engine = create_engine(DATABASE_URL)

local_session = sessionmaker(autoflush=False, autocommit=False, bind=engine)


class Base(DeclarativeBase):
    pass

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()