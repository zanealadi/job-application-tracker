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
@app.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    # check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    hashed_password = get_password_hash(password)
    new_user = User(email=email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "New user created",
        "user": {
            "id": new_user.id,
            "email": new_user.email
        }
    }


# login and get access token
@app.post("/token")
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
@app.post("/applications")
def create_application(company: str, position: str, status: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_app = JobApplication(
        user_id=current_user.id, # this links to the logged in user
        company=company,
        position=position,
        status=status
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
@app.get("/applications")
def get_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applications = db.query(JobApplication).filter(JobApplication.user_id == current_user.id).all()
    return {"count": len(applications), "applications": applications}

# get applications be id
@app.get("/applications/{app_id}")
def get_application_with_id(app_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id, JobApplication.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

# update an application
@app.put("/application/{app_id}")
def update_application(app_id: int, status: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id, JobApplication.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app.status = status
    db.commit()
    return {"message": "Application Updated!", "application": app}

# delete an application
@app.delete("/application/{app_id}")
def delete_application(app_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id, JobApplication.user_id == current_user.id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(app)
    db.commit()
    return {"message": "Application Deleted!"}

# get info about the currently logged in user
@app.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email
    }