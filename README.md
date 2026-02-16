# Saspirant

> Smart job alert platform for Indian competitive exam aspirants. Never miss a government job deadline again.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://saspirant.vercel.app)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🎯 Problem & Solution

**Problem:** Indian exam aspirants miss government job deadlines because notifications are scattered across 100+ websites.

**Solution:** Saspirant monitors official recruitment sites 24/7, filters opportunities by your eligibility (age, education, exam type), and sends personalized email alerts.

## ✨ Features

- **Smart Monitoring** - Automated scraping of UPSC, SSC, universities, and other official sites
- **Intelligent Filtering** - Only get alerts for jobs matching your age, qualification, and preferences
- **Email Alerts** - Instant notifications via SendGrid when opportunities are posted
- **Google OAuth** - Sign in with Google or traditional email/password
- **Dashboard** - Track all alerts, deadlines, and monitored websites in one place
- **Manual Scraping** - Trigger immediate checks on any website

## 🛠 Tech Stack

**Frontend:** HTML, CSS (Tailwind), JavaScript  
**Backend:** Flask 3.0, Python 3.11  
**Database:** PostgreSQL (Neon)  
**Authentication:** Flask sessions + Google OAuth (Authlib)  
**Scraping:** BeautifulSoup4, Selenium, pdfplumber  
**Email:** SendGrid API  
**Scheduler:** APScheduler (periodic scraping)  
**Deployment:** Vercel (frontend) + Render (backend)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (or Neon account)
- SendGrid account
- Google OAuth credentials (optional)

### Local Setup

1. **Clone & Install**
```bash
git clone https://github.com/swarn6402/saspirant.git
cd saspirant/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure Environment**

Create `backend/.env`:

```env
DATABASE_URL=postgresql://user:pass@host/db
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=your_email@example.com
FLASK_SECRET_KEY=your_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret
```

3. **Initialize Database**

```bash
flask init-db
```

4. **Run Servers**

```bash
# Backend (Terminal 1)
cd backend
python app.py  # Runs on :5000

# Frontend (Terminal 2)
cd frontend
python -m http.server 3000  # Runs on :3000
```

5. **Open App**

```
http://localhost:3000/templates/index.html
```

## 📦 Project Structure

```
saspirant/
├── backend/
│   ├── routes/          # API endpoints (auth, preferences, dashboard)
│   ├── services/        # Email, scraping, matching logic
│   ├── scrapers/        # Site-specific scrapers (UPSC, SSC, universities)
│   ├── models.py        # Database models
│   └── app.py           # Flask application
├── frontend/
│   ├── templates/       # HTML pages
│   └── static/          # CSS, JS, images
└── README.md
```

## 🔑 Key API Endpoints

```
POST   /api/auth/register              # Email/password registration
POST   /api/auth/login                 # Email/password login
GET    /api/auth/google/login          # Google OAuth login
POST   /api/preferences/{user_id}      # Save exam preferences
GET    /api/dashboard/{user_id}/summary # Dashboard data
POST   /api/dashboard/{user_id}/trigger-scrape/{url_id}  # Manual scrape
```

## 🌐 Deployment

**Frontend (Vercel):**

* Root Directory: `frontend`
* Build Command: (none - static site)
* Deploy: Auto-deploys from `main` branch

**Backend (Render):**

* Root Directory: `backend`
* Build Command: `pip install -r requirements.txt`
* Start Command: `gunicorn app:app`
* Add environment variables in dashboard

**Database:** Neon PostgreSQL (serverless)

## 🔒 Security

* Passwords hashed with Werkzeug (bcrypt)
* Google OAuth with state validation
* CORS configured for specific origins
* Environment variables for all secrets
* HTTPS in production

## 📊 How It Works

1. User registers and sets preferences (exam types, age, qualification)
2. User adds official recruitment website URLs to monitor
3. APScheduler runs scrapers every 6 hours (configurable)
4. Scrapers extract job notifications from websites + PDFs
5. Matching engine filters jobs by user eligibility
6. SendGrid sends email alerts for matching opportunities
7. Dashboard displays all alerts and deadlines

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 👤 Author

**Swarnjeet Nath Tiwary**

* Portfolio: [swarn6402.vercel.app](https://swarn6402.vercel.app)
* GitHub: [@swarn6402](https://github.com/swarn6402)
* LinkedIn: [swarn6402](https://linkedin.com/in/swarn6402)

## 🙏 Acknowledgments

Built for millions of Indian competitive exam aspirants who deserve equal opportunity.

---

**⭐ Star this repo if it helped you!**
