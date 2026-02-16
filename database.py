from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv

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
    company = Column(String)
    position = Column(String) 
    status = Column(String) 

    # each application belongs to one user
    user = relationship("User", back_populates="applications")

# creates the table in the db
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created!")