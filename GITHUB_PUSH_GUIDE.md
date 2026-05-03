# 📤 Push Updated Code to GitHub

## Step-by-Step Instructions

### Prerequisites
- Git installed on your machine
- Access to your repository
- Changes already tested locally ✅

---

## Option 1: Using PowerShell (Recommended)

### **Step 1: Navigate to Project Directory**
```powershell
cd "d:\7th Semester\Student Mental Health Companion"
```

### **Step 2: Check Git Status**
```powershell
git status
```

You should see:
```
On branch main
Changes not staged for commit:
  modified:   requirements.txt
  modified:   services/gemini_service.py
  
Untracked files:
  API_KEY_SETUP.md
  TECHNICAL_CHANGES.md
  API_KEY_DEPLOYMENT_GUIDE.md
```

### **Step 3: Stage All Changes**
```powershell
git add -A
```

Or be specific:
```powershell
git add requirements.txt
git add services/gemini_service.py
git add API_KEY_SETUP.md
git add TECHNICAL_CHANGES.md
git add API_KEY_DEPLOYMENT_GUIDE.md
```

### **Step 4: Verify Staged Changes**
```powershell
git status
```

You should see "Changes to be committed" (green).

### **Step 5: Commit Changes**
```powershell
git commit -m "Fix: Update google-generativeai to v0.13.0 and fix API compatibility issues

- Upgrade google-generativeai from 0.8.3 to 0.13.0 to fix Content type error
- Fix chat history format for new API version
- Improve error messages with actionable guidance
- Add comprehensive deployment guides for GitHub, Local, and Render
- Fixes issue: 'API_KEY_INVALID' and 'Content type not found' errors"
```

### **Step 6: Push to GitHub**
```powershell
git push origin main
```

---

## Option 2: Using VS Code Git Integration

1. Open VS Code in your project folder
2. Click **Source Control** icon (left sidebar)
3. Review changes under **Changes**
4. Click **+** icon to stage all files
5. Type commit message in the **Message** box:
   ```
   Fix: Update google-generativeai to v0.13.0 and fix API compatibility
   ```
6. Click **Commit** button
7. Click **Sync Changes** to push

---

## What Gets Pushed

### ✅ Files Being Updated
```
📝 requirements.txt
   └─ google-generativeai: 0.8.3 → 0.13.0

📝 services/gemini_service.py
   └─ Fixed chat_with_gemini() function
   └─ Fixed history format for new API
   └─ Improved error messages

📝 API_KEY_SETUP.md (NEW)
   └─ Setup guide for developers

📝 TECHNICAL_CHANGES.md (NEW)
   └─ Documentation of all changes

📝 API_KEY_DEPLOYMENT_GUIDE.md (NEW)
   └─ Deployment guide for Local/GitHub/Render
```

### ❌ Files NOT Being Pushed
```
.env ← Protected by .gitignore ✅
.git/ ← Version control folder
__pycache__/ ← Python cache
instance/ ← Database
mental_health.db ← Local database
```

---

## Verify Push Success

After pushing, check your GitHub:
1. Go to: https://github.com/Bilal-Nazeer-Dev/student-mental-health-companion
2. Click **<> Code** tab
3. You should see:
   - ✅ Recent commit message
   - ✅ Updated `requirements.txt`
   - ✅ Updated `services/gemini_service.py`
   - ✅ New documentation files

---

## Complete Terminal Commands (Copy-Paste)

```powershell
# Navigate to project
cd "d:\7th Semester\Student Mental Health Companion"

# Check status
git status

# Stage all changes
git add -A

# Commit with message
git commit -m "Fix: Update google-generativeai to v0.13.0 and fix API compatibility issues

- Upgrade google-generativeai from 0.8.3 to 0.13.0 to fix Content type error
- Fix chat history format for new API version
- Improve error messages with actionable guidance
- Add comprehensive deployment guides
- Fixes: API_KEY_INVALID and Content type errors"

# Push to GitHub
git push origin main

# Verify
git log --oneline -5
```

---

## ⚠️ If You Get Authentication Error

### For HTTPS (Personal Access Token)
1. Go to: https://github.com/settings/tokens
2. Create **Personal Access Token** (repo scope)
3. Use token as password when prompted

### For SSH (Recommended)
```powershell
# Generate SSH key (if not already done)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add to GitHub: https://github.com/settings/keys
cat ~/.ssh/id_ed25519.pub | clip

# Change remote to SSH
git remote set-url origin git@github.com:Bilal-Nazeer-Dev/student-mental-health-companion.git

# Test connection
ssh -T git@github.com
```

---

## ✅ After Pushing

### Next: Update Render Deployment
1. Go to https://dashboard.render.com
2. Select your service
3. Click **"Redeploy"** (pull latest code from GitHub)
4. Wait for deployment to complete
5. Test at your Render URL

### Next: Update Local Render API Key (If Not Done)
If not already done:
1. Go to Render Dashboard → Settings
2. Add Environment Variable:
   ```
   GEMINI_API_KEY = your_new_key_here
   ```
3. Save (auto-redeploys)

---

## 🐛 Troubleshooting

**Q: "fatal: not a git repository"**
A: Make sure you're in the correct directory with `.git` folder

**Q: "nothing to commit, working tree clean"**
A: Changes already committed. Check git log with `git log --oneline -5`

**Q: "Your branch is ahead of origin/main by X commits"**
A: Run `git push origin main` to sync

**Q: "Permission denied (publickey)"**
A: Use HTTPS with token or setup SSH keys

---

## 📋 Final Checklist

- [ ] Navigated to correct directory
- [ ] Ran `git status` to verify changes
- [ ] Staged changes with `git add -A`
- [ ] Committed with meaningful message
- [ ] Pushed with `git push origin main`
- [ ] Verified changes on GitHub website
- [ ] (Optional) Redeployed on Render

---

**You're all set!** Your updated code is now on GitHub. 🎉
