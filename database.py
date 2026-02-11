from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:Platypus1234$@localhost:5432/jobtracker"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# define table in db
class JobApplication(Base):
    __tablename__ = "applications" # name of table

    id = Column(Integer, primary_key=True, index=True) # auto incrementing id
    company = Column(String) # company name
    position = Column(String) # title of position
    status = Column(String) # things like applied, rejected, etc

# creates the table in the db
Base.metadata.create_all(bind=engine)