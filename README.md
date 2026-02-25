# Job Application Tracker API

A job application REST API with JWT Authentication, mock web-scraping, and PostgreSQL database - All deployed on AWS.

**Live API**: http://54.87.136.106:8000
**Interactive API Documentation**: http://54.87.136.106:8000/docs

## Features
**User Authentication** - Secure JWT token-based authentication with bcrypt password hashing
**Job Application Management** - Full CRUD operations with status tracking
**Web Scraping** - Automated job discovery from job boards with duplicate prevention
**Status Workflow** - Track applications from Wishlist → Applied → Interview → Offer
**Rate Limiting** - Protected against abuse (5 registrations/min, 10 scrapes/hour)
**Database Migrations** - Version-controlled schema changes with Alembic  
**Data Validation** - Pydantic schemas with automatic API documentation  
**User Isolation** - Each user only sees their own applications

## Tech Stack

**Backend**
- FastAPI (Python 3.11) - Modern async web framework
- PostgreSQL - Relational database with SQLAlchemy ORM
- JWT Authentication - python-jose with bcrypt hashing
- Pydantic - Data validation and serialization
- BeautifulSoup - Web scraping engine
- SlowAPI - Rate limiting protection

**Infrastructure**
- **AWS ECS Fargate** - Serverless container orchestration
- **AWS RDS** - Managed PostgreSQL with automated backups
- **AWS ECR** - Private Docker image registry
- **Docker** - Containerized deployment
- **Alembic** - Database migration management

## Architecture
```
Internet → ECS Fargate (FastAPI Container) → RDS PostgreSQL
              ↑
            ECR (Docker Images)
```

## API Endpoints

### Public Endpoints
- `POST /register` - Create new user account
- `POST /token` - Login and receive JWT token

### Protected Endpoints (Requires Authentication)
**Applications**
- `GET /applications/` - List all your applications
- `POST /applications/` - Create new application
- `GET /applications/{id}` - Get specific application details
- `PUT /applications/{id}` - Update application status/details
- `DELETE /applications/{id}` - Remove application

**Job Scraping**
- `POST /scrape/jobs` - Scrape jobs from job boards (rate limited: 10/hour)
- `GET /scraped-jobs/` - View all scraped jobs
- `POST /scraped-jobs/{id}/convert` - Convert scraped job to tracked application

**User**
- `GET /me` - Get current user information

## Database Schema

### Users
- Email-based authentication
- Secure password hashing with bcrypt
- One-to-many relationship with applications

### Applications
**Core Fields:**
- Company, position, status (enum-validated)
- Job URL, notes, salary range
- Applied date, created/updated timestamps

**Status Options:**
- `wishlist` - Jobs you're interested in
- `applied` - Applications submitted
- `phone_screen` - Initial phone screening
- `interview` - In interview process
- `offer` - Offer received
- `rejected` - Application rejected
- `accepted` - Offer accepted

### Scraped Jobs
- Title, company, location, URL, description
- Source tracking (Mock)
- Unique URL constraint prevents duplicates
- Convertible to tracked applications

## Security Features

**Authentication & Authorization**
- JWT tokens with 30-minute expiration
- Bcrypt password hashing (cost factor 12)
- User data isolation at database level

**Rate Limiting**
- Registration: 5 attempts/minute per IP
- Login: 10 attempts/minute per IP
- Job scraping: 10 requests/hour per IP
- General endpoints: 100 requests/minute default

**Infrastructure Security**
- Environment variable management for secrets
- VPC with security groups
- HTTPS-ready (HTTP currently for demo)
- CORS middleware configured

## Local Development Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/zanealadi/job-application-tracker.git
cd job-application-tracker
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create `.env` file:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:password@localhost:5432/jobtracker
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=jobtracker
```

5. **Start PostgreSQL with Docker**
```bash
docker-compose up -d
```

6. **Run database migrations**
```bash
alembic upgrade head
```

7. **Start the API**
```bash
uvicorn main:app --reload
```

Visit **http://localhost:8000/docs** for interactive API documentation.

## Deployment

The application is deployed on AWS using:

- **ECS Fargate** - Serverless container hosting (no server management)
- **RDS PostgreSQL** - Managed database with automated backups and multi-AZ
- **ECR** - Private Docker registry
- **VPC & Security Groups** - Network isolation and access control
- **CloudWatch Logs** - Centralized logging and monitoring

**Cost Protection:**
- Budget alerts set at $20/month
- Rate limiting prevents abuse
- Single container (scalable to more if needed)

## Project Highlights

- **Production deployment** - Live on AWS, not just localhost
- **Professional authentication** - Industry-standard JWT + bcrypt
- **Database migrations** - Version-controlled schema like real companies
- **Rate limiting** - Protected against abuse and DDoS
- **User isolation** - Proper multi-tenant data separation
- **Automatic documentation** - FastAPI generates interactive API docs
- **Docker containerization** - Consistent deployment anywhere
- **RESTful design** - Follows API best practices

## Future Enhancements

Potential features for v2.0:
- [ ] Email notifications for application deadlines (AWS SES)
- [ ] Background job scraping with Celery + Redis
- [ ] React/Vue.js frontend with authentication
- [ ] Application analytics dashboard
- [ ] Resume attachment storage (AWS S3)
- [ ] Calendar integration for interview scheduling
- [ ] Chrome extension for one-click job saving
- [ ] Company research notes with AI summarization

## Learning Outcomes

This project demonstrates proficiency in:
- **API Development** - RESTful design, authentication, validation
- **Database Design** - Relationships, migrations, indexing
- **Security** - JWT auth, password hashing, rate limiting, data isolation
- **DevOps** - Docker, AWS (ECS, RDS, ECR), CI/CD concepts
- **Software Architecture** - Separation of concerns, scalability
- **Documentation** - Auto-generated API docs, clear README

## Cost Considerations

**Estimated AWS costs:**
- ECS Fargate (1 container): ~$10-15/month
- RDS db.t3.micro: ~$15/month (free tier eligible for 6 months)
- **Total: ~$25/month** (under $10/month with free tier)

**To minimize costs:**
- Scale to 0 when not actively demoing: `aws ecs update-service ... --desired-count 0`
- Budget alerts configured at $20/month
- Rate limiting prevents abuse

## Testing

**Test the live API:**

1. Register: `POST http://54.87.136.106:8000/register`
2. Login: `POST http://54.87.136.106:8000/token`
3. Create application: `POST http://54.87.136.106:8000/applications/`

Or use the interactive documentation at http://54.87.136.106:8000/docs

**Alert**
API AWS IP would not work in my browser so Postman was used to verify functionality

## License

MIT License - Feel free to use this for learning!