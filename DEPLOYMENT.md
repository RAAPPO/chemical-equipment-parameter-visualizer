# 🚀 Deployment Guide

Complete guide for deploying Chemical Equipment Parameter Visualizer to production.

## 📋 Table of Contents

1. <a>Architecture Overview</a>
2. <a>Prerequisites</a>
3. <a>Backend Deployment (Koyeb)</a>
4. <a>Frontend Deployment (Cloudflare Pages)</a>
5. <a>Custom Domain Configuration</a>
6. <a>Environment Variables</a>
7. <a>Database Setup</a>
8. <a>SSL/TLS Configuration</a>
9. <a>Monitoring and Maintenance</a>
10. <a>Troubleshooting</a>

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────┐
│  FRONTEND: Cloudflare Pages                      │
│  ├─ React 19.2.0 + Vite 7.2.4                   │
│  ├─ Global CDN distribution                      │
│  ├─ Auto SSL/TLS                                 │
│  └─ Custom Domain: cepv.raappo.cf                │
└────────────────┬─────────────────────────────────┘
                 │ HTTPS API Calls
                 ▼
┌──────────────────────────────────────────────────┐
│  BACKEND: Koyeb                                  │
│  ├─ Django 5.1.6 + DRF 3.15.2                   │
│  ├─ Gunicorn WSGI Server                         │
│  ├─ Python 3.10                                  │
│  ├─ Scale-to-zero + Auto-scaling                │
│  └─ Custom Domain: api-cepv.raappo.cf           │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────┐
│  DATABASE: PostgreSQL (Koyeb Managed)           │
│  ├─ Version 16                                   │
│  ├─ Automated backups                            │
│  ├─ High availability                            │
│  └─ Free tier: 1 GB storage                     │
└──────────────────────────────────────────────────┘

DNS Management: Cloudflare
SSL/TLS: Auto-provisioned (Let's Encrypt)
Cost: $0/month (Free tiers)
```

---

## ✅ Prerequisites

### Required Accounts
- ✅ GitHub account (for repository access)
- ✅ Koyeb account (<a href="https://app.koyeb.com">app.koyeb.com</a>)
- ✅ Cloudflare account (<a href="https://dash.cloudflare.com">dash.cloudflare.com</a>)
- ✅ Domain name (optional, but recommended)

### Repository Setup
- ✅ Code pushed to GitHub
- ✅ `.python-version` file in `backend/` directory (must contain `3.10`)
- ✅ `requirements.txt` includes all dependencies
- ✅ `frontend-web/` ready for Vite build

---

## 🔧 Backend Deployment (Koyeb)

### Step 1: Create Koyeb Account

1. Visit <a href="https://app.koyeb.com">app.koyeb.com</a>
2. Sign up with GitHub
3. Authorize Koyeb to access your repositories
4. Add credit card (required for verification, free tier won't charge)

### Step 2: Create PostgreSQL Database

1. In Koyeb dashboard, click "**Database**"
2. Click "**Create Database**"
3. Configure:
   - **Engine:** PostgreSQL
   - **Name:** `cepv-db`
   - **Version:** 16
   - **Region:** Frankfurt (or closest to you)
   - **Plan:** **Starter (Free)**
4. Click "**Create Database**"
5. Wait ~2 minutes for provisioning
6. Copy **Internal Connection String** (starts with `postgres://...`)

### Step 3: Connect GitHub Repository

1. Click "**Create**" → "**Web Service**"
2. Select "**GitHub**" as source
3. If first time:
   - Click "**Connect GitHub Account**"
   - Select repositories: `chemical-equipment-parameter-visualizer`
   - Click "**Install &amp; Authorize**"
4. Select your repository
5. Select branch: `main`

### Step 4: Configure Build Settings

```
Builder: Buildpack
Root path: backend
Build command: (leave empty - auto-detected)
Run command: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

### Step 5: Configure Service

```
Instance Type: Starter (Free)
Region: Frankfurt (same as database)
Scaling:
  - Min instances: 0 (scale-to-zero)
  - Max instances: 1
Health Check:
  - Path: /api/health/
  - Port: 8000
```

### Step 6: Add Environment Variables

Click "**Add variable**" and add these:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | `django-insecure-change-this-to-something-random-and-secure` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.koyeb.app,api-cepv.raappo.cf` |
| `CORS_ALLOWED_ORIGINS` | `https://cepv.raappo.cf` |
| `DATABASE_URL` | [Paste PostgreSQL connection string from Step 2] |
| `PYTHON_VERSION` | `3.10` |

### Step 7: Deploy

1. Click "**Deploy**"
2. Wait 3-5 minutes for build
3. Monitor logs for any errors
4. Once deployed, you'll get a URL: `https://your-service-name.koyeb.app`

### Step 8: Run Database Migrations

1. In Koyeb dashboard, click your service
2. Click "**Shell**" tab
3. Wait for shell to load
4. Run commands:

```bash
python manage.py migrate
python manage.py createsuperuser
# Username: admin, Password: admin123
python manage.py shell
```

```python
from django.contrib.auth.models import User
User.objects.create_user('testuser', 'test@example.com', 'testpass123')
exit()
```

### Step 9: Test Backend

```bash
curl https://your-service-name.koyeb.app/api/health/
# Expected: {"status":"healthy"}

curl -X POST https://your-service-name.koyeb.app/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
# Expected: {"access":"...","refresh":"..."}
```

---

## 🌐 Frontend Deployment (Cloudflare Pages)

### Step 1: Login to Cloudflare Pages

1. Visit <a href="https://pages.cloudflare.com">pages.cloudflare.com</a>
2. Login with your Cloudflare account
3. Ensure your domain is added to Cloudflare DNS

### Step 2: Create New Project

1. Click "**Create a project**"
2. Select "**Connect to Git**"
3. Choose "**GitHub**"
4. Authorize Cloudflare Pages
5. Select repository: `chemical-equipment-parameter-visualizer`

### Step 3: Configure Build Settings

```
Project name: cepv
Production branch: main
Framework preset: Vite
Root directory: frontend-web
Build command: npm run build
Build output directory: dist
```

### Step 4: Add Environment Variables

Click "**Add variable**":

| Variable Name | Value |
|---------------|-------|
| `VITE_API_BASE_URL` | `https://api-cepv.raappo.cf/api` |
| `NODE_VERSION` | `18` |

### Step 5: Deploy

1. Click "**Save and Deploy**"
2. Wait 3-5 minutes for build
3. Monitor build logs
4. Once deployed, you'll get a URL: `https://cepv.pages.dev`

### Step 6: Test Frontend

1. Open `https://cepv.pages.dev` in browser
2. You should see login page
3. Try logging in with `testuser` / `testpass123`
4. If login fails, check CORS settings in backend

---

## 🌐 Custom Domain Configuration

### Backend Domain (api-cepv.raappo.cf)

#### In Koyeb:
1. Go to your service → "**Settings**" → "**Domains**"
2. Click "**Add domain**"
3. Enter: `api-cepv.raappo.cf`
4. Copy the CNAME target shown (e.g., `your-service.koyeb.app`)

#### In Cloudflare DNS:
1. Go to your domain → "**DNS**" → "**Records**"
2. Click "**Add record**"
3. Configure:
   - **Type:** CNAME
   - **Name:** `api-cepv`
   - **Target:** [Koyeb CNAME from above]
   - **Proxy status:** ✅ Proxied (orange cloud)
   - **TTL:** Auto
4. Save and wait 2-3 minutes

#### Verify:
```bash
curl https://api-cepv.raappo.cf/api/health/
# Should return: {"status":"healthy"}
```

### Frontend Domain (cepv.raappo.cf)

#### In Cloudflare Pages:
1. Go to your project → "**Custom domains**"
2. Click "**Set up a custom domain**"
3. Enter: `cepv.raappo.cf`
4. Cloudflare auto-configures DNS
5. Wait for "**Active**" status (~2 minutes)

#### Verify:
```bash
curl -I https://cepv.raappo.cf
# Should return: 200 OK
```

---

## 🔐 Environment Variables Reference

### Backend (.env)

```env
# Security
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False

# Domains
ALLOWED_HOSTS=.koyeb.app,api-cepv.raappo.cf
CORS_ALLOWED_ORIGINS=https://cepv.raappo.cf

# Database (automatically provided by Koyeb)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Python
PYTHON_VERSION=3.10

# Optional
JWT_ACCESS_TOKEN_LIFETIME_HOURS=24
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
MAX_UPLOAD_SIZE_MB=10
```

### Frontend (.env.production)

```env
VITE_API_BASE_URL=https://api-cepv.raappo.cf/api
NODE_VERSION=18
```

---

## 🗄️ Database Setup

### Automatic Backup
Koyeb automatically backs up PostgreSQL databases daily.

### Manual Backup
```bash
# In Koyeb Shell
pg_dump $DATABASE_URL > backup.sql
```

### Restore from Backup
```bash
psql $DATABASE_URL < backup.sql
```

---

## 🔒 SSL/TLS Configuration

### Automatic SSL
Both Koyeb and Cloudflare provide automatic SSL/TLS:
- **Cloudflare:** Uses Universal SSL (Let's Encrypt)
- **Koyeb:** Auto-provisions certificates

### Force HTTPS
Django settings already configured (lines 179-189 in settings.py):
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
```

### Test SSL
```bash
# Check SSL grade
curl https://www.ssllabs.com/ssltest/analyze.html?d=api-cepv.raappo.cf
curl https://www.ssllabs.com/ssltest/analyze.html?d=cepv.raappo.cf
```

---

## 📊 Monitoring and Maintenance

### Koyeb Monitoring
- View metrics: Service → "**Metrics**" tab
- Check logs: Service → "**Logs**" tab
- Monitor database: Database → "**Metrics**"

### Cloudflare Analytics
- Pages dashboard shows build history
- Analytics tab shows traffic stats

### Health Checks
Set up external monitoring:
```bash
# Cron job to check health every 5 minutes
*/5 * * * * curl https://api-cepv.raappo.cf/api/health/
```

---

## 🐛 Troubleshooting

### Backend Issues

#### Build Fails
**Error:** `psycopg2-binary compilation failed`
**Solution:** Ensure `.python-version` file exists with content `3.10`

#### Database Connection Error
**Error:** `could not connect to server`
**Solution:** Verify `DATABASE_URL` is correct in environment variables

#### CORS Error
**Error:** `blocked by CORS policy`
**Solution:** Check `CORS_ALLOWED_ORIGINS` includes frontend domain

### Frontend Issues

#### Blank Page
**Error:** Frontend loads but shows blank
**Solution:** Check browser console for API connection errors

#### API Not Found
**Error:** `404` on API calls
**Solution:** Verify `VITE_API_BASE_URL` in Cloudflare Pages environment variables

#### Build Fails
**Error:** `npm install` fails
**Solution:** Check `NODE_VERSION` environment variable is set to `18`

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Code pushed to GitHub `main` branch
- [ ] `.python-version` file present in `backend/`
- [ ] All dependencies in `requirements.txt` and `package.json`
- [ ] Local testing passed

### Backend (Koyeb)
- [ ] Koyeb account created
- [ ] PostgreSQL database created
- [ ] GitHub repository connected
- [ ] Build settings configured
- [ ] Environment variables added
- [ ] Service deployed successfully
- [ ] Database migrations ran
- [ ] Test users created
- [ ] Health check passes
- [ ] Custom domain configured

### Frontend (Cloudflare Pages)
- [ ] Cloudflare account ready
- [ ] Project created and connected
- [ ] Build settings configured
- [ ] Environment variables added
- [ ] Build successful
- [ ] Custom domain configured
- [ ] Frontend loads correctly
- [ ] API connection working

### Final Verification
- [ ] Login works on production
- [ ] CSV upload functional
- [ ] Charts render correctly
- [ ] PDF download works
- [ ] HTTPS enforced on both domains
- [ ] CORS configured properly
- [ ] Admin panel accessible
- [ ] All API endpoints working

---

## 📞 Support

For deployment issues:
- **Koyeb Docs:** https://www.koyeb.com/docs
- **Cloudflare Pages Docs:** https://developers.cloudflare.com/pages
- **Project Issues:** https://github.com/RAAPPO/chemical-equipment-parameter-visualizer/issues

---

