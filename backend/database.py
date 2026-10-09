import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Boolean, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class VerifiedEntityRecord(Base):
    __tablename__ = "verified_entities"

    entity_id = Column(String, primary_key=True, index=True)
    concept_name = Column(String, index=True)
    verified_definition = Column(Text)
    confidence_score = Column(Float)
    needs_human_review = Column(Boolean, default=False)
    citations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
