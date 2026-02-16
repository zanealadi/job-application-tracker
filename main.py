from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import SessionLocal, JobApplication, User, Base, engine
from auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from schemas import (
    UserCreate, UserResponse, Token,
    ApplicationCreate, ApplicationUpdate, ApplicationResponse, ApplicationListResponse
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
        status=application.status
    )

    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return {"message": "Application Created!", "application" : {
        "id": new_app.id,
        "company": new_app.company,
        "position": new_app.position,
        "status": new_app.status
    }}

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
@app.put("/application/{app_id}", response_model=ApplicationResponse)
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

    db.commit()
    db.refresh(app)
    return app

# delete an application
@app.delete("/application/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
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