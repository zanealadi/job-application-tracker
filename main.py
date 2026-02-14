from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, JobApplication, Base, engine

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

# root endpoint
@app.get("/")
def read_root():
    return {"message": "Job Application Tracker API", "docs": "/docs"}

# add a new job application
@app.post("/applications")
def create_application(company: str, position: str, status: str, db: Session = Depends(get_db)):
    new_app = JobApplication(
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
def get_applications(db: Session = Depends(get_db)):
    applications = db.query(JobApplication).all()
    return {"count": len(applications), "applications": applications}

# get applications be id
@app.get("/applications/{app_id}")
def get_application_with_id(app_id: int, db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

# update an application
@app.put("/application/{app_id}")
def update_application(app_id: int, status: str, db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app.status = status
    db.commit()
    return {"message": "Application Updated!", "application": app}

# delete an application
@app.delete("/application/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(app)
    db.commit()
    return {"message": "Application Deleted!"}
