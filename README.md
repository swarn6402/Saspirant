# Saspirant

> Smart job alert platform for Indian competitive exam aspirants. Never miss a government job deadline again.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://saspirant.vercel.app)
[![React](https://img.shields.io/badge/react-18.3-blue)](https://react.dev)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

Saspirant monitors 50+ government recruitment websites 24/7 and sends personalized email alerts for jobs matching your age, qualification, and exam preferences. Built for millions of Indian competitive exam aspirants who can't afford to miss a single deadline.

## Key Features

- **Smart Filtering** - Matching by age, education, exam category, and location
- **24/7 Monitoring** - Automated scraping every 6 hours across UPSC, SSC, Railways, Banking, State PSCs, and Universities
- **Instant Alerts** - Email notifications via SendGrid for matching opportunities
- **Dual Authentication** - Google OAuth or email/password
- **Live Dashboard** - Track alerts, deadlines, and monitoring status in real-time
- **Manual Triggers** - Test scrape any website on-demand

## Tech Stack

**Frontend:** React 18.3, Vite, React Router, Context API, Tailwind CSS

**Backend:** Flask 3.0, SQLAlchemy, PostgreSQL (Neon), Google OAuth 2.0, APScheduler

**Scraping & Email:** BeautifulSoup4, Selenium, pdfplumber, SendGrid

**Deployment:** Vercel (frontend), Render (backend), Neon (database)

## Quick Start

**1. Clone Repository**
```bash
git clone https://github.com/swarn6402/Saspirant.git
cd Saspirant
```

**2. Backend Setup**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```env
DATABASE_URL=postgresql://user:pass@host/db
SENDGRID_API_KEY=your_key
SENDGRID_FROM_EMAIL=your@email.com
FLASK_SECRET_KEY=your_secret
GOOGLE_CLIENT_ID=your_google_id
GOOGLE_CLIENT_SECRET=your_google_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/google/callback
FRONTEND_URL=http://localhost:5173
```

**3. Frontend Setup**
```bash
cd frontend/react-app
npm install
```

**4. Run Servers**
```bash
# Terminal 1 - Backend
cd backend && python app.py

# Terminal 2 - Frontend
cd frontend/react-app && npm run dev
```

Open `http://localhost:5173`

## Project Structure

```
Saspirant/
+-- backend/
¦   +-- routes/          # Auth, preferences, dashboard API endpoints
¦   +-- services/        # Email, scraping, matching logic
¦   +-- scrapers/        # Site-specific scrapers
¦   +-- models.py        # Database models
¦   +-- app.py           # Flask application entry point
+-- frontend/
¦   +-- react-app/       # React + Vite application (active)
¦   +-- static/          # Legacy static assets (backup)
¦   +-- templates/       # Legacy HTML templates (backup)
+-- README.md
```

## API Endpoints

```
POST  /api/auth/register
POST  /api/auth/login
GET   /api/auth/google/login
GET   /api/auth/google/callback
POST  /api/preferences/{user_id}
POST  /api/preferences/{user_id}/urls
GET   /api/preferences/{user_id}/urls
GET   /api/dashboard/{user_id}/summary
GET   /api/dashboard/{user_id}/alerts
POST  /api/dashboard/{user_id}/trigger-scrape/{url_id}
```

## Deployment

| | Frontend | Backend |
|---|---|---|
| Platform | Vercel | Render |
| Branch | `react-frontend` | `main` |
| Root | `frontend/react-app` | `backend` |
| Build | `npm run build` | `pip install -r requirements.txt` |
| Output | `dist` | `gunicorn app:app` |

## Author

**Swarnjeet Nath Tiwary**
- Portfolio: [swarn6402.vercel.app](https://swarn6402.vercel.app)
- GitHub: [@swarn6402](https://github.com/swarn6402)
- LinkedIn: [swarn6402](https://linkedin.com/in/swarn6402)
- Twitter: [@swarn6402](https://x.com/swarn6402)

---
Built for millions of Indian competitive exam aspirants who deserve equal opportunity.
