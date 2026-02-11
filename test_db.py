from database import SessionLocal, JobApplication

# create session
db = SessionLocal()

# create a new job application
new_job =  JobApplication(
    company="Amazon",
    position="Software Engineer Intern",
    status="Applied"
)

# add to database
db.add(new_job)
db.commit() # save

print("Jobs application added!")

# query all applications
applications = db.query(JobApplication).all()

print("\nAll applications in the database:")
for app in applications:
    print(f"- {app.company}: {app.position} ({app.status})")

db.close()