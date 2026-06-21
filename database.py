from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/mydatabase"

engine = create_engine()

local_session = sessionmaker(autoflush = False , autocommit = False ,  bind = engine  )