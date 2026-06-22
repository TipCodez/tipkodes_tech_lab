# TIPKODES TECH LAB

TIPKODES TECH LAB is a full-stack Django and Bootstrap 5 portfolio platform for cybersecurity findings, Python growth, cloud computing notes, software projects, blogs, videos, gallery images, certificates, skills, resume/CV, and contact messages.

The project is admin-powered, responsive, animated, media-ready, and designed as a personal technology lab rather than a simple static portfolio.

## Features

- Django Admin content management for all major modules
- Projects with categories, career tracks, screenshots, GitHub, live demo, video, and PDF documentation
- Cybersecurity findings with severity badges, ethical disclaimer, reports, screenshots, filters, and search
- Python career posts for scripts, automation tools, Django apps, APIs, snippets, and notes
- Cloud computing posts for providers, architecture diagrams, deployment notes, and cloud security
- Blog system with categories, tags, featured posts, reading time, and share links
- Gallery with image modal previews and category filters
- YouTube video embeds with detail pages
- Certificates with images, PDFs, credential IDs, and verification links
- Skills grouped by category and linked to projects
- Online resume/CV page with downloadable PDF
- Contact form that saves messages in the database
- Optional contact email notifications when SMTP environment variables are configured
- Global search across projects, blogs, findings, videos, certificates, gallery, Python, and cloud posts
- Advanced search with type, date range, sorting, and highlighted terms
- Newsletter subscriptions
- Page-view analytics
- Content reactions
- Generated project report PDF downloads
- Certificate verification by credential ID
- Testimonials and learning timeline pages
- GitHub and YouTube profile integration records
- Deployment and system architecture page
- Pagination, custom 404/500 pages, media upload validation, and production-ready environment variables

## Tech Stack

- Backend: Django
- Frontend: HTML, CSS, Bootstrap 5, JavaScript
- Database: SQLite for development, PostgreSQL-ready through `DATABASE_URL`
- Admin: Django Admin
- Static files: Whitenoise-ready
- Media: Local Django media folder, Cloudinary-ready for future upgrade

## Project Structure

```text
tipkodes_tech_lab/
|-- manage.py
|-- requirements.txt
|-- .env.example
|-- config/
|-- core/
|-- templates/
|-- static/
|-- media/
```

## Windows Setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_lab_sample
python manage.py runserver
```

Open the website:

```text
http://127.0.0.1:8000/
```

Open Django Admin:

```text
http://127.0.0.1:8000/admin/
```

## Environment Variables

Copy `.env.example` to `.env` for your deployment host and set:

- `SECRET_KEY`
- `DEBUG`
- `USE_MANIFEST_STATIC` (`True` only after running `collectstatic` for production)
- `ENABLE_NGROK` (`True` when testing through an ngrok public URL)
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- Cloudinary variables for future media storage
- `SECURE_SSL_REDIRECT` and `SECURE_HSTS_SECONDS` for HTTPS-only production deployments

The current settings read environment variables directly. For local development, defaults are provided so the project can run immediately after installing requirements.

## Internet Testing With ngrok

Set this in your environment when exposing the local Django server through ngrok:

```powershell
$env:ENABLE_NGROK="True"
python manage.py runserver 127.0.0.1:8000
ngrok http 8000
```

Ngrok hostnames are allowed by default through `ENABLE_NGROK=True`. Set `ENABLE_NGROK=False` only when you want to disable ngrok host support. Restart Django after changing environment variables.

## Admin Usage Guide

1. Create categories first. Choose the correct category type for each module.
2. Add profile and resume records.
3. Add career tracks for cybersecurity, Python, cloud, web development, AI, research, and software engineering.
4. Add projects, screenshots, findings, blog posts, gallery images, videos, certificates, and skills.
5. Mark selected projects, blogs, videos, certificates, or cloud posts as featured to show them on the home page.
6. Review contact messages in Django Admin and mark them as read.

## Screenshots

Add screenshots in `static/images/` or upload live screenshots through the Gallery and ProjectImage models.

## Future Improvements

- PostgreSQL production database
- Cloudinary media storage
- Custom admin dashboard
- Dark/light mode toggle
- Visitor analytics
- Newsletter subscription
- Blog comments
- Two-factor admin login
- Email notifications
- Rate limiting
- Koyeb, Render, PythonAnywhere, or other cloud deployment

## Author

TIPKODES

Cybersecurity, Python, Cloud Computing, and Real-World Tech Projects.
