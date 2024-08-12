from sqlalchemy import Column, Integer, String, Text, DateTime, LargeBinary, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine('sqlite:///instances/todos.db')
Session = sessionmaker(bind=engine)
session = Session()

class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    time = Column(DateTime, nullable=False)
    images = Column(LargeBinary, nullable=True)
    done = Column(Boolean, default=False)

Base.metadata.create_all(engine)
