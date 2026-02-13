# Testing Checklist

## Backend Tests
- [ ] Run: python backend/seed_test_data.py
- [ ] Run: python backend/test_all_endpoints.py
- [ ] All tests pass?

## Frontend Tests (Browser)
- [ ] Landing page loads (http://127.0.0.1:3000/templates/index.html)
- [ ] Registration works
- [ ] Preferences save correctly
- [ ] Dashboard displays stats
- [ ] Dashboard shows recent alerts (after seeding data)
- [ ] Manual scrape button works
- [ ] No console errors

## Database Tests
- [ ] Check users table has entries
- [ ] Check job_notifications table has entries
- [ ] Check sent_alerts table has entries
- [ ] Check monitored_urls table has entries

## Email Test (Optional)
- [ ] Trigger manual scrape
- [ ] Check if email received (if matching notification found)

## Performance
- [ ] Dashboard loads in < 2 seconds
- [ ] Scraper completes in < 30 seconds
- [ ] No memory leaks (backend stable after multiple scrapes)

## Ready for Deployment?
- [ ] All backend tests pass
- [ ] All frontend flows work
- [ ] No console errors
- [ ] Database persists correctly
