# Deploying to Render

This guide will help you deploy your Django application to Render.

## Prerequisites

1. A GitHub account (or GitLab/Bitbucket)
2. A Render account (sign up at https://render.com)

## Step 1: Push to GitHub

1. Initialize git repository (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Create a repository on GitHub and push:
   ```bash
   git remote add origin <your-github-repo-url>
   git branch -M main
   git push -u origin main
   ```

## Step 2: Create Database on Render

1. Go to your Render dashboard
2. Click "New +" → "PostgreSQL"
3. Name it `matibashoe-db`
4. Select the free plan
5. Note the database connection details

## Step 3: Deploy Web Service

### Option A: Using render.yaml (Recommended)

1. Go to Render dashboard
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and create the services

### Option B: Manual Setup

1. Go to Render dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `matibashoe`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r DesertHero/requirements.txt && cd DesertHero && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `cd DesertHero && gunicorn Matibashoe.wsgi:application`
   - **Root Directory**: Leave empty (or set to project root)

5. Add Environment Variables:
   - `SECRET_KEY`: Generate a new secret key (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com,*.onrender.com`
   - `DATABASE_URL`: Copy from your PostgreSQL database service (Render auto-provides this if linked)
   - `EMAIL_HOST`: `smtp.gmail.com`
   - `EMAIL_PORT`: `587`
   - `EMAIL_USE_TLS`: `True`
   - `EMAIL_HOST_USER`: Your Gmail address
   - `EMAIL_HOST_PASSWORD`: Your Gmail app password (not your regular password)

6. Link the PostgreSQL database you created in Step 2

## Step 4: Create Superuser

After deployment, you'll need to create a superuser:

1. Go to your service on Render
2. Click on "Shell" tab
3. Run:
   ```bash
   cd DesertHero
   python manage.py createsuperuser
   ```

## Important Notes

- **Media Files**: Files uploaded to `/media/` will be lost on each deploy. Consider using cloud storage (AWS S3, Cloudinary) for production.
- **Static Files**: Static files are automatically collected and served via WhiteNoise.
- **Database**: The free PostgreSQL plan has limitations. Consider upgrading for production use.
- **Email**: Make sure to use a Gmail App Password, not your regular password. Enable 2FA and generate an app password.

## Troubleshooting

- If static files aren't loading, check that `collectstatic` ran successfully in the build logs
- If database connection fails, verify `DATABASE_URL` is set correctly
- Check build logs for any errors during deployment

## Security Reminders

- Never commit `SECRET_KEY` or passwords to git
- Use environment variables for all sensitive data
- Keep `DEBUG=False` in production

