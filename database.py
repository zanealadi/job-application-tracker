from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv
from datetime import datetime
from schemas import ApplicationStatus

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in environment variables!")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# user model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # relationship is one user has many applications
    applications = relationship("JobApplication", back_populates="user")


# job application model
class JobApplication(Base):
    __tablename__ = "applications" # name of table

    id = Column(Integer, primary_key=True, index=True) # auto incrementing id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company = Column(String, nullable=False)
    position = Column(String, nullable=False) 
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.WISHLIST) 
    job_url = Column(String, nullable=True) # link to job posting
    notes = Column(Text, nullable=True) # whatever notes user has about the job
    applied_date = Column(DateTime, nullable=True)
    salary_range = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now) # automatically sets on creation
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # each application belongs to one user
    user = relationship("User", back_populates="applications")

class ScrapedJob(Base):
    __tablename__ = "scraped_jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=True)
    url = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    posted_date = Column(DateTime, nullable=True)
    source = Column(String, nullable=False)
    scraped_at = Column(DateTime, default=datetime.now)

# creates the table in the db
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created!")