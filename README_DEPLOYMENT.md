# Deployment Checklist

## Pre-Deployment Steps

1. Create Neon.tech PostgreSQL database
   - Sign up at https://neon.tech
   - Create new project
   - Copy connection string (DATABASE_URL)
   - Format: postgresql://user:password@host/database

2. Create SendGrid account
   - Sign up at https://sendgrid.com
   - Verify sender email address
   - Create API key
   - Copy API key

3. Push code to GitHub
   - git init
   - git add .
   - git commit -m "Initial commit"
   - git remote add origin your-github-repo-url
   - git push -u origin main

4. Create Render account
   - Sign up at https://render.com
   - Connect your GitHub account

## Deployment Steps

1. In Render dashboard click "New +" then "Blueprint"
2. Connect your GitHub repository
3. Render will auto-detect render.yaml and show two services
4. Set environment variables for saspirant-backend:
   - DATABASE_URL: paste from Neon
   - SENDGRID_API_KEY: paste from SendGrid
   - SENDGRID_FROM_EMAIL: your verified email
   - FLASK_SECRET_KEY: auto-generated
5. Click "Apply" to start deployment (takes about 5 minutes)
6. Once deployed go to saspirant-backend service
7. Click "Shell" tab
8. Run: flask init-db
9. Visit the frontend URL to test

## Post-Deployment Testing

1. Open the frontend URL
2. Register a test user
3. Add preferences
4. Add a URL to monitor
5. Trigger manual scrape to verify everything works

## Troubleshooting

- If database errors occur check DATABASE_URL is correct
- If emails don't send verify SENDGRID_API_KEY and sender email
- Check logs in Render dashboard for detailed error messages
- Use /health endpoint to check system status

This configuration deploys both frontend and backend to Render's free tier.
