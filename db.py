from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

engine = create_engine('sqlite:///database.db', connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)
Base = declarative_base()

class FileRecord(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)           # short key (eg: uuid)
    channel_message_id = Column(Integer)        # message id in private channel
    file_type = Column(String)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class LinkGroup(Base):
    __tablename__ = "links"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)           # group key (for /link)
    file_keys = Column(Text)                    # comma separated file keys
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(engine)
