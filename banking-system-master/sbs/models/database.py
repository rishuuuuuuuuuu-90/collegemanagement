from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeMeta

SQL_URI = "mysql+pymysql://root:root@localhost/banking_system"
# SQL_URI = "mysql+pymysql://sabaa:mybankingsystem@sabaa.mysql.pythonanywhere-services.com/sabaa$banking_system"
engine = create_engine(url=SQL_URI)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base: DeclarativeMeta = declarative_base()
