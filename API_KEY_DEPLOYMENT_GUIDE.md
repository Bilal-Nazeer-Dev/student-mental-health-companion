# 🔐 API Key Management Across GitHub, Local IDE & Render

## ⚠️ SECURITY RULE #1
**NEVER push your API key to GitHub!** Anyone can use it and steal your quota.

---

## 📍 Where to Update API Key?

### 1️⃣ **Local IDE** (Your Computer)
Update your **local `.env` file**:
```env
GEMINI_API_KEY=your_actual_key_here
SECRET_KEY=sage-super-secret-key-2024
DATABASE_PATH=mental_health.db
DEBUG=True
```

**Location:** `d:\7th Semester\Student Mental Health Companion\.env`

**Used for:** Testing locally on your machine
- `python app.py` or `python run.py`
- http://localhost:5000

---

### 2️⃣ **GitHub** (Remote Repository)
**DO NOT** push `.env` file to GitHub!

Your `.gitignore` should already include:
```
.env
.env.local
instance/
__pycache__/
*.db
```

**What to do instead:**
1. Keep `.env.example` in GitHub (template only, no real keys)
2. Other developers copy it: `cp .env.example .env`
3. They add their own API key locally

**Current `.env.example` content:**
```env
# Copy this file to .env and fill in your values
GEMINI_API_KEY=your_key_here
SECRET_KEY=change-this-to-a-long-random-string
DATABASE_PATH=mental_health.db
DEBUG=True
```

---

### 3️⃣ **Render** (Production Server)
Use **Environment Variables** (NOT `.env` file):

#### **Step 1: Go to Render Dashboard**
https://dashboard.render.com

#### **Step 2: Find Your Service**
- Click on your Flask app service
- Go to **Settings** tab
- Scroll to **Environment** section

#### **Step 3: Add Environment Variables**
Click **"Add Environment Variable"** and add:

| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | `your_actual_key_here` |
| `SECRET_KEY` | `your-secure-random-string` |
| `DATABASE_PATH` | `mental_health.db` |
| `DEBUG` | `False` |

#### **Step 4: Deploy**
- Click **"Save"** (auto-deploys with new env vars)
- Wait for deployment to complete
- Test on Render URL

---

## 🔄 Summary: API Key Locations

```
┌─────────────────────────────────────────────────────┐
│                 YOUR PROJECT                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  LOCAL IDE                                          │
│  └─ .env (REAL KEY) ← You use this                 │
│     GEMINI_API_KEY=AIza...                         │
│                                                     │
│  GITHUB                                             │
│  └─ .env.example (NO KEY) ← Template only          │
│     GEMINI_API_KEY=                                │
│  └─ .gitignore ← Prevents pushing .env             │
│                                                     │
│  RENDER (Production)                                │
│  └─ Environment Variables (Web UI) ← Set here      │
│     GEMINI_API_KEY=AIza...                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## ✅ Checklist

### For Local Development
- [ ] `.env` file exists in project root
- [ ] Contains real `GEMINI_API_KEY=AIza...`
- [ ] Run `python app.py` and test locally
- [ ] `.env` is in `.gitignore` (never committed)

### For GitHub
- [ ] `.env.example` exists (template only)
- [ ] Real `.env` is NOT in repository
- [ ] `.gitignore` includes `.env`
- [ ] Other developers can clone and copy `.env.example` to `.env`

### For Render Production
- [ ] Environment variables set in Render dashboard
- [ ] Same keys as `.env` (minus the file itself)
- [ ] Secrets are NOT in code, only in Render UI
- [ ] Auto-deploy after setting env vars

---

## 🚀 Complete Workflow

### 1. **Developer (You) - Local Setup**
```bash
# Clone from GitHub
git clone https://github.com/your-username/student-mental-health.git
cd student-mental-health

# Create .env from template
cp .env.example .env

# Add your real API key
# Edit .env: GEMINI_API_KEY=AIza_YOUR_REAL_KEY

# Install & test locally
pip install -r requirements.txt
python app.py
# Test at http://localhost:5000 ✅
```

### 2. **Push to GitHub** (Safe)
```bash
# Make changes, commit
git add .
git commit -m "Fix API compatibility"
git push origin main

# ✅ .env is NOT pushed (protected by .gitignore)
# ✅ Only .env.example is there
```

### 3. **Deploy to Render** (Production)
```
1. Go to https://dashboard.render.com
2. Select your Flask service
3. Settings → Environment Variables
4. Add: GEMINI_API_KEY=AIza_YOUR_REAL_KEY
5. Click Save (auto-deploys)
6. Test at your-app.onrender.com ✅
```

### 4. **Other Developers Can Clone**
```bash
git clone https://github.com/your-username/student-mental-health.git
cp .env.example .env
# They edit .env with their own API key
pip install -r requirements.txt
python app.py
```

---

## ⚡ Quick Reference

| Environment | Method | API Key Visible? | Committed to Git? |
|-------------|--------|------------------|------------------|
| **Local IDE** | `.env` file | ✅ Yes (private) | ❌ No (.gitignore) |
| **GitHub** | None (template only) | ❌ No | ✅ .env.example |
| **Render** | Web UI (Settings) | ❌ Hidden | ❌ No |

---

## 🔒 Security Best Practices

✅ **DO:**
- Keep API key in `.env` locally
- Add `.env` to `.gitignore`
- Use environment variables in Render
- Use different keys for dev/prod (optional)
- Rotate keys periodically

❌ **DON'T:**
- Push `.env` to GitHub
- Hardcode API key in Python files
- Share keys in Slack/Email
- Use same key across all environments (risky)
- Commit `.env` by mistake

---

## 🚨 If You Accidentally Pushed the Key

1. **Delete the key immediately** from Google Cloud (revoke it)
2. **Create a new API key**
3. **Force push history** (advanced):
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch .env' \
   --prune-empty --tag-name-filter cat -- --all
   git push origin --force --all
   ```
4. Update new key in:
   - Local `.env`
   - Render environment variables

---

## 📞 Summary

**Your current setup:**
- ✅ `.env` is in `.gitignore` (good!)
- ✅ `.env.example` exists as template
- ⏳ Need to: Set env vars in Render dashboard

**Three steps to complete:**
1. Local: Update `.env` with new API key
2. GitHub: Already safe (no changes needed)
3. Render: Set `GEMINI_API_KEY` in Environment Variables → Deploy

Done! Your app will work everywhere. 💙
