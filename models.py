from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, INTEGER, String, DateTime



engine = create_engine("postgresql+psycopg2://postgres:danila2001@localhost:5432/TeleBot", echo = True)
Base = declarative_base()

class Item(Base):
    __tablename__ = "item"
    
    
    plan = Column(INTEGER, ForeignKey("plan.id_plan"))
    id_item = Column(INTEGER, primary_key = True)
    item = Column(String(1000))
    time_create = Column(DateTime, default = datetime.now())
    time_end = Column(DateTime, default=None)

    plan_i = relationship("Plan",back_populates="item")


class Plan(Base):
    __tablename__ = "plan"
    
    
    id_plan = Column(INTEGER, primary_key = True)
    time_create = Column(DateTime, default = datetime.now())
    time_end = Column(DateTime, default = None)
    user = Column(INTEGER, ForeignKey("my_user.id_user"))
    
    item = relationship("Item", back_populates="plan_i")
    my_user = relationship("User",back_populates="plan")

class User(Base):
    __tablename__ = "my_user"
    
    
    id_user = Column(INTEGER, primary_key = True, unique = True)
    id_user_telegram = Column(String(200))
    plan = relationship("Plan",back_populates="my_user")

Base.metadata.create_all(engine)
