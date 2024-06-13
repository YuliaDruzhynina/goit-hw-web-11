from sqlalchemy import create_engine, Column, Integer, String, Date

from db import Base, engine

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String(150))
    phone_number = Column(String(20))
    email = Column(String(150), unique=True, index=True)
    birthday = Column(Date) 


Base.metadata.create_all(bind=engine)
