# Saspirant - Job Alert Platform for Indian Competitive Exams

Saspirant is a job alert platform that aggregates notifications for Indian competitive exams (such as UPSC and SSC), matches them to user preferences, and sends alerts.

## Tech Stack

- Backend: Python + Flask
- Database: PostgreSQL (Neon.tech)
- Scheduler: APScheduler
- Email: SendGrid API
- Frontend: HTML/CSS/JavaScript with Tailwind CSS
- Scraping: BeautifulSoup4, Selenium, pdfplumber

## Setup Instructions

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install backend dependencies:
   - `pip install -r backend/requirements.txt`
4. Copy `.env.example` to `.env` and update values as needed.

## Run Locally

1. From project root, ensure environment variables are loaded.
2. Start the Flask app:
   - `python backend/app.py`
3. Open your browser and navigate to your local Flask URL.

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (Neon.tech)
- `SENDGRID_API_KEY` - SendGrid API key
- `SENDGRID_FROM_EMAIL` - Sender email used by SendGrid
- `FLASK_SECRET_KEY` - Flask secret key
- `FLASK_ENV` - Flask environment (`development`/`production`)
