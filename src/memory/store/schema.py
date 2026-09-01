from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MemoryRow(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    relation = Column(String, nullable=False)
    value = Column(String, nullable=False)
    status = Column(String, nullable=False)
    importance = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=True)
    supersedes_memory_id = Column(Integer, nullable=True)
    source_message_id = Column(String, nullable=False)
    embedding = Column(Text, nullable=True)
