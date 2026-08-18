# CINTRACON v2.0 Backend

CINTRACON v2.0 Backend is a Django REST API for the CINTRACON platform. It powers authentication, student profiles, posts, note sharing, job opportunities, announcements, events, maintenance mode, notifications, real-time channels, and an AI chat assistant.

## Tech Stack

- Python
- Django
- Django REST Framework
- Simple JWT authentication
- PostgreSQL
- Redis, Channels, and Celery
- Cloudinary media storage
- SMTP email delivery
- OpenAI/LangChain based chat service
- WhiteNoise static file serving

## Main Features

- Custom user authentication and JWT login
- Email verification and password reset OTP flow
- Student directory and profile management
- Home feed posts, reactions, reports, bookmarks, and sharing metadata
- Note sharing with file uploads and public share links
- Job opportunity posts with public detail links
- Upcoming events and announcements
- Maintenance mode controls
- Real-time notifications through Django Channels
- AI chat assistant with PDF-based context fallback support

## Project Structure

```text
cintracon_backend/   Django project settings, URLs, ASGI/WSGI, middleware
users/               Authentication, profiles, verification, user APIs
home/                Feed posts, reactions, reports, bookmarks
allstudents/         Student listing APIs
jobopportunities/    Job post APIs
notesharing/         Note upload, listing, download tracking
announcement/        Announcement APIs
upcomingevents/      Event APIs
maintenance/         Maintenance mode APIs
notifications/       Notification models, consumers, routing
chat/                AI chat sessions and service
documents/           PDF context document for the AI assistant
templates/           Email and share templates
static/              Static assets
```

## Environment Variables

This project must be configured through environment variables. Do not commit real credentials.

Create a local `.env` file from `.env.example` and fill the values in your local machine or hosting provider dashboard.

Required or commonly used variables:

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
DATABASE_URL
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
REDIS_URL
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
EMAIL_HOST
EMAIL_PORT
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
EMAIL_USE_SSL
EMAIL_USE_TLS
DEFAULT_FROM_EMAIL
OPENAI_API_KEY
```

## Local Setup

1. Create and activate a virtual environment.

```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Create your local environment file.

```powershell
copy .env.example .env
```

4. Add your real local values to `.env`.

5. Run migrations.

```powershell
python manage.py migrate
```

6. Start the development server.

```powershell
python manage.py runserver
```

For ASGI/WebSocket development, you can run Daphne:

```powershell
daphne -b 127.0.0.1 -p 8000 cintracon_backend.asgi:application
```

## API Routes

Main route groups:

```text
/api/auth/
/api/home/
/api/all-students/
/api/job-opportunities/
/api/note-sharing/
/api/chat/
/api/announcement/
/api/events/
/api/maintenance/
/api/admin/
/api/notifications/
```

Public share/detail routes:

```text
/api/notes/public/<note_id>/
/api/jobs/public/<job_id>/
/api/events/public/<event_id>/
/share/post/<post_id>/
/share/note/<note_id>/
/share/job/<job_id>/
/share/event/<event_id>/
```

## Deployment Notes

- Set all environment variables in the hosting provider dashboard.
- Keep `DEBUG=False` in production.
- Add production backend domains to `ALLOWED_HOSTS`.
- Add frontend domains to `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`.
- Configure PostgreSQL through `DATABASE_URL` when available.
- Configure Redis through `REDIS_URL` for cache, Channels, and Celery.
- Run migrations before serving production traffic.
- Run collectstatic if required by the deployment platform.

## Security Notes

- Never commit `.env` or any real credential file.
- Rotate credentials immediately if they were ever pushed publicly.
- Keep `.env.example` placeholder-only.
- Use provider dashboards or secret managers for production values.
- After removing exposed secrets from Git history, force-push the cleaned history only when you understand the impact.

## Useful Commands

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

## License

This project is maintained for CINTRACON. Add a license file if the repository will be distributed publicly.
