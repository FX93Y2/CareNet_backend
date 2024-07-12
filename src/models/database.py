from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(String, primary_key=True)
    location_x = Column(Float)
    location_y = Column(Float)
    tasks = relationship("Task", back_populates="sensor")

class Worker(Base):
    __tablename__ = 'workers'
    id = Column(String, primary_key=True)
    name = Column(String)
    tasks = relationship("Task", back_populates="worker")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    sensor_id = Column(String, ForeignKey('sensors.id'))
    worker_id = Column(String, ForeignKey('workers.id'))
    priority = Column(Integer)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.now(datetime.timezone(datetime.timedelta(hours=8)))) # UTC+8 China Standard Time
    sensor = relationship("Sensor", back_populates="tasks")
    worker = relationship("Worker", back_populates="tasks")