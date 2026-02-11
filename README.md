# Job Application Tracker

A smart job application tracking system with automated job scraping and email reminders. Used to track internship applications.

## Features (In Progress)
- Track job applications with status updates
- PostgreSQL database with Docker
- FastAPI REST API
- Automated email reminders
- Job scraping from LinkedIn/Indeed (Maybe more in the future)
- AWS deployment

## Tech Stack
- **Backend:** FastAPI (Using Python)
- **Database:** PostgreSQL
- **Task Queue:** Celery + Redis
- **Deployment:** Docker, AWS (ECS, RDS, SQS)

## Current Progress
- Basic FastAPI setup
- Docker and PostgreSQL connection
- Database models
- API endpoints (In progress)
- Background tasks (Not started yet)
- Web scraping (Not started yet)
- AWS deployment (Not started yet)

## Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary

# Start database
docker-compose up -d

# Run API
uvicorn main:app --reload
```
## Learning Goals
Building this project to learn:
- FastAPI and REST API design
- Database design with PostgreSQL
- Background task processing
- Docker containerization
- AWS cloud deployment