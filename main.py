from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import SessionLocal, JobApplication, User, Base, engine, ScrapedJob
from typing import Optional
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from scraper import IndeedScraper, MockScraper
from schemas import (
    UserCreate, UserResponse, Token,
    ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationListResponse, ApplicationStatus,
    ScrapedJobResponse, ScrapedJobListResponse
)

# creates the tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Job Application Tracker")

# dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# PUBLIC ENDPOINTS

# root endpoint
@app.get("/")
def read_root():
    return {"message": "Job Application Tracker API", 
            "docs": "/docs",
            "endpoints": {
                "register": "POST /register",
                "login": "POST /token",
                "applications": "GET/POST /applications (requires auth)"
            }}


# register a new user
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
    


# login and get access token
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # find user by email
    user = db.query(User).filter(User.email == form_data.username).first()

    # verify user exists and the password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# PROTECTED ENDPOINTS (AUTH REQUIRED)

# add a new job application
@app.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(application: ApplicationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_app = JobApplication(
        user_id=current_user.id, # this links to the logged in user
        company=application.company,
        position=application.position,
        status=application.status,
        job_url=application.job_url,
        notes=application.notes,
        applied_date=application.applied_date,
        salary_range=application.salary_range
    )

    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

# get all applications
@app.get("/applications", response_model=ApplicationListResponse)
def get_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applications = db.query(JobApplication).filter(JobApplication.user_id == current_user.id).all()
    return {"count": len(applications), "applications": applications}

# get applications by id
@app.get("/applications/{app_id}", response_model=ApplicationResponse)
def get_application_with_id(app_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id, JobApplication.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

# update an application
@app.put("/applications/{app_id}", response_model=ApplicationResponse)
def update_application(app_id: int, application_update: ApplicationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id, JobApplication.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application_update.company is not None:
        app.company = application_update.company
    if application_update.position is not None:
        app.position = application_update.position
    if application_update.status is not None:
        app.status = application_update.status
    if application_update.job_url is not None:
        app.job_url = application_update.job_url
    if application_update.notes is not None:
        app.notes = application_update.notes
    if application_update.applied_date is not None:
        app.applied_date = application_update.applied_date
    if application_update.salary_range is not None:
        app.salary_range = application_update.salary_range

    db.commit()
    db.refresh(app)
    return app

# delete an application
@app.delete("/applications/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(app_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id, JobApplication.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(app)
    db.commit()
    return None

# get info about the currently logged in user
@app.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# SCRAPING
@app.post("/scrape/jobs", response_model=ScrapedJobListResponse)
def scrape_jobs(
    query: str = "software engineer intern", 
    location: str = "", max_results: int = 10, 
    use_mock: bool = True, 
    current_user: Session = Depends(get_current_user), 
    db: Session = Depends(get_db)):

    # choose scraper
    scraper = MockScraper() if use_mock else IndeedScraper()

    scraped_jobs = scraper.search_jobs(query, location, max_results)
    saved_jobs = []
    duplicates = 0

    for job_data in scraped_jobs:
        # check if jobs exists already using url
        existing = db.query(ScrapedJob).filter(ScrapedJob.url == job_data["url"]).first()
        if existing:
            duplicates += 1
            continue
        
        # create new scraped job
        new_job = ScrapedJob(
            title=job_data["title"],
            company=job_data["company"],
            location=job_data.get("location"),
            url=job_data["url"],
            description=job_data.get("description"),
            source=job_data["source"]
        )
        db.add(new_job)
        saved_jobs.append(new_job)
    db.commit()

    # refresh saved jobs to get id's
    for job in saved_jobs:
        db.refresh(job)
    
    return {
        "count": len(saved_jobs),
        "jobs": saved_jobs
    }

# get scraped jobs from database
@app.get("/scraped-jobs/", response_model=ScrapedJobListResponse)
def get_scraped_jobs(
    skip: int = 0,
    limit: int = 50,
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    query = db.query(ScrapedJob)

    if source:
        query = query.filter(ScrapedJob.source == source)
    
    jobs = query.order_by(ScrapedJob.scraped_at.desc()).offset(skip).limit(limit).all()
    return {"count": len(jobs), "jobs": jobs}

# convert scraped job into application tracker
@app.post("/scraped-jobs/{job_id}/convert")
def convert_to_application(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scraped_job = db.query(ScrapedJob).filter(ScrapedJob.id == job_id).first()

    if not scraped_job:
        raise HTTPException(status_code=404, detail="Scraped job not found")
    
    # create application from scraped job
    new_app = JobApplication(
        user_id=current_user.id,
        company=scraped_job.company,
        position=scraped_job.title,
        status=ApplicationStatus.WISHLIST,
        job_url=scraped_job.url,
        notes=f"Found via scraping from {scraped_job.source}"
    )

    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return{"message": "Converted to application!", "application_id": new_app.id}