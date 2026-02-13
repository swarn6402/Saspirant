# Saspirant - Smart Job Alert Platform for Competitive Exams

> Never miss a government job or exam deadline again. Saspirant monitors official recruitment websites 24/7 and sends you personalized email alerts for opportunities matching your qualifications.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Solution](#-solution)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Problem Statement

Students and professionals preparing for competitive exams in India face a critical challenge:

- **Fragmented Information**: Government recruitment notifications are scattered across 100+ websites (UPSC, SSC, State PSCs, Universities, Banking, Railways, etc.)
- **Manual Tracking**: Aspirants must manually check each website daily to avoid missing deadlines
- **Spam Alerts**: Existing job alert services send irrelevant notifications, creating inbox clutter
- **Missed Opportunities**: A single missed deadline can mean waiting another year for the next exam cycle

**The Cost**: Thousands of aspirants miss application deadlines every year, losing opportunities worth lakhs in salary and career growth.

---

## 💡 Solution

**Saspirant** is an intelligent job alert system that:

1. **Monitors** official recruitment websites automatically (24/7 scheduled scraping)
2. **Filters** opportunities based on your exact qualifications (age, education, exam preferences)
3. **Alerts** you via email only when truly relevant jobs are posted
4. **Tracks** all your alerts in a centralized dashboard

**Key Differentiator**: Zero spam - you only receive alerts for jobs you're actually eligible for and interested in.

---

## ✨ Features

### For Users
- **Personalized Monitoring**: Select specific exam categories (UPSC, SSC, Banking, State PSCs, Universities, etc.)
- **Smart Filtering**: Set age limits, qualification requirements, and location preferences
- **Multi-Source Tracking**: Monitor multiple official websites simultaneously
- **Email Alerts**: Instant notifications when matching opportunities are posted
- **Dashboard**: View all alerts, deadlines, and monitoring status in one place
- **Manual Scraping**: Trigger immediate checks on any monitored website

### Technical Features
- **Intelligent Web Scraping**: Handles diverse website structures (HTML, PDF notifications, dynamic content)
- **PDF Parsing**: Automatically extracts details from recruitment PDFs
- **Matching Engine**: Sophisticated logic to match jobs with user eligibility criteria
- **Scheduled Tasks**: APScheduler runs periodic scraping (configurable intervals)
- **Email Delivery**: SendGrid integration for reliable email delivery
- **Database Persistence**: PostgreSQL for robust data storage

---

## 🛠 Tech Stack

### Backend
- **Framework**: Flask 3.0 (Python web framework)
- **Database**: PostgreSQL (via Neon.tech for production)
- **ORM**: SQLAlchemy 3.1
- **Task Scheduler**: APScheduler 3.10
- **Web Scraping**: 
  - BeautifulSoup4 (HTML parsing)
  - Selenium (dynamic content)
  - pdfplumber (PDF text extraction)
- **Email**: SendGrid API
- **Server**: Gunicorn (production WSGI server)

### Frontend
- **HTML/CSS/JavaScript** (Vanilla JS, no frameworks)
- **Styling**: Tailwind CSS (utility-first CSS)
- **UI Components**: Custom-built responsive components

### Infrastructure
- **Hosting**: 
  - Frontend: Vercel (static hosting)
  - Backend: PythonAnywhere (Python hosting with scheduler support)
- **Database**: Neon (serverless PostgreSQL)
- **Email Service**: SendGrid (100 emails/day free tier)

---

```
## 🏗 Architecture
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│  (Landing Page → Registration → Preferences → Dashboard)     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK REST API                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth Routes  │  │ Preferences  │  │  Dashboard   │      │
│  │   /api/auth  │  │/api/preferences│ │/api/dashboard│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    CORE SERVICES LAYER                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │ Scraper Service  │  │ Matching Service │  │   Email   │ │
│  │  (Web Scraping)  │  │ (Job Filtering)  │  │  Service  │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   APSCHEDULER (Cron Jobs)                    │
│          Runs scraping tasks every 6 hours (configurable)    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  POSTGRESQL DATABASE                         │
│  Tables: users, preferences, monitored_urls,                 │
│          job_notifications, sent_alerts                      │
└─────────────────────────────────────────────────────────────┘
```

### Workflow

1. **User Registration**: User provides name, email, DOB, qualification
2. **Preference Setup**: User selects exam categories and adds URLs to monitor
3. **Scheduled Scraping**: APScheduler runs scrapers every 6 hours for each monitored URL
4. **Data Extraction**: Scrapers fetch notifications, parse PDFs, extract job details
5. **Matching**: Matching engine compares jobs with user eligibility (age, qualification, categories)
6. **Alert Delivery**: If match found → Send email via SendGrid → Record in database
7. **Dashboard Display**: User sees all alerts, stats, and can trigger manual scrapes

---

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- PostgreSQL database (or Neon.tech account)
- SendGrid account (for email alerts)

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/swarn6402/saspirant.git
cd saspirant
```

2. **Set up backend**
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Create .env file in backend/ directory
cp .env.example .env

# Edit .env with your credentials:
DATABASE_URL=postgresql://user:password@host/database
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_verified_email@example.com
FLASK_SECRET_KEY=generate_a_random_secret_key
FLASK_ENV=development
```

4. **Initialize database**
```bash
flask init-db
```

5. **Run the application**
```bash
# Start backend server
python app.py
# Backend runs on http://127.0.0.1:5000

# In a new terminal, start frontend
cd ../frontend
python -m http.server 3000
# Frontend runs on http://127.0.0.1:3000
```

6. **Access the application**
- Open browser: `http://127.0.0.1:3000/templates/index.html`

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `SENDGRID_API_KEY` | SendGrid API key for emails | `SG.xxxxxxxxxxxxxxx` |
| `SENDGRID_FROM_EMAIL` | Verified sender email | `alerts@saspirant.com` |
| `FLASK_SECRET_KEY` | Flask session secret key | `random_string_here` |
| `FLASK_ENV` | Environment (development/production) | `production` |

### Scraper Configuration

Modify scraping frequency in `backend/services/scheduler_service.py`:
```python
# Default: every 6 hours
scheduler.add_job(scrape_and_notify, 'interval', hours=6)
```

---

## 📖 Usage

### For End Users

1. **Register**: Create account with name, email, DOB, qualification
2. **Set Preferences**: 
   - Select exam categories (UPSC, SSC, Banking, etc.)
   - Optionally set age range and location preferences
3. **Add URLs**: Add official recruitment website URLs to monitor
4. **Receive Alerts**: Get email notifications when matching jobs are posted
5. **Dashboard**: View all alerts, trigger manual scrapes, manage preferences

### For Developers

#### Add a New Scraper

1. Create scraper in `backend/scrapers/`:
```python
from .base_scraper import BaseScraper

class NewSiteScraper(BaseScraper):
    def scrape(self):
        # Your scraping logic
        notifications = []
        # ... extract and parse
        return notifications
```

2. Register in `backend/scrapers/__init__.py`:
```python
def get_scraper(url, scraper_type=None):
    if 'newsite.com' in url:
        return NewSiteScraper()
    # ... other scrapers
```

#### Run Tests
```bash
# Backend API tests
cd backend
python test_all_endpoints.py

# Seed test data
python seed_test_data.py
```

---

## 🔌 API Documentation

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "date_of_birth": "2000-01-01",
  "highest_qualification": "Graduate"
}

Response: 201 Created
{
  "message": "User registered successfully",
  "user_id": 1
}
```

#### Get User
```http
GET /api/auth/user/{user_id}

Response: 200 OK
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "qualification": "Graduate"
}
```

### Preferences

#### Add/Update Preferences
```http
POST /api/preferences/{user_id}
Content-Type: application/json

{
  "exam_categories": ["UPSC", "SSC"],
  "min_age": 21,
  "max_age": 35,
  "preferred_locations": ["All India"]
}

Response: 200 OK
{
  "message": "Preferences updated",
  "preferences": {...}
}
```

#### Add Monitored URL
```http
POST /api/preferences/{user_id}/urls
Content-Type: application/json

{
  "url": "https://upsc.gov.in/examinations/active",
  "website_name": "UPSC Official",
  "scraper_type": "html"
}

Response: 201 Created
```

### Dashboard

#### Get Dashboard Summary
```http
GET /api/dashboard/{user_id}/summary

Response: 200 OK
{
  "user": {...},
  "stats": {
    "total_alerts_received": 15,
    "alerts_this_week": 3,
    "monitored_urls": 4
  },
  "recent_alerts": [...]
}
```

#### Trigger Manual Scrape
```http
POST /api/dashboard/{user_id}/trigger-scrape/{url_id}

Response: 200 OK
{
  "message": "Scrape completed",
  "notifications_found": 5,
  "new_notifications": 2,
  "alerts_sent": 1
}
```

---

## 🚀 Deployment

### Production Deployment (Vercel + PythonAnywhere)

#### Frontend (Vercel)
1. Push code to GitHub
2. Import repository in Vercel
3. Set build settings:
   - Root Directory: `frontend`
   - No build command needed (static site)
4. Deploy

#### Backend (PythonAnywhere)
1. Create PythonAnywhere account
2. Upload code or clone from GitHub
3. Set up virtual environment and install requirements
4. Configure WSGI file
5. Set environment variables in dashboard
6. Initialize database: `flask init-db`
7. Set up scheduled task for scraping

### Environment-Specific Settings

Production `render.yaml` provided for easy deployment on Render (alternative to PythonAnywhere).

---

## 🧪 Testing

### Run All Tests
```bash
cd backend

# Test all API endpoints
python test_all_endpoints.py

# Seed sample data
python seed_test_data.py
```

### Manual Testing Checklist
- [ ] User registration works
- [ ] Preferences can be set and updated
- [ ] URLs can be added and removed
- [ ] Dashboard loads with correct stats
- [ ] Manual scrape finds notifications
- [ ] Email alerts are sent (check inbox)
- [ ] No console errors in browser

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions
- Write tests for new features

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Swarnjeet Nath Tiwary** - *Initial work* - [GitHub Profile](https://github.com/swarn6402)

---

## 🙏 Acknowledgments

- Inspired by the needs of millions of competitive exam aspirants in India
- Thanks to the open-source community for excellent libraries (Flask, BeautifulSoup, etc.)
- Special thanks to government bodies for maintaining public recruitment portals

---

## 📞 Contact

- Email: swarnjeettiwary01@gmail.com
- Project Link: [https://github.com/swarn6402/saspirant](https://github.com/swarn6402/saspirant)

---

## 🗺️ Roadmap

- [ ] Add support for 50+ more exam websites
- [ ] Mobile app (React Native)
- [ ] WhatsApp alerts integration
- [ ] AI-powered eligibility prediction
- [ ] Community forum for aspirants
- [ ] Premium features (priority alerts, advanced filtering)

---

**Made with ❤️ for aspirants, by aspirants**

---
