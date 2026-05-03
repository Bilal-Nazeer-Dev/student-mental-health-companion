# 🔑 API Key Setup Guide

## ⚠️ Current Issues

Your app is reporting:
1. **API Key Invalid Error** — Your current API key is no longer valid
2. **Module 'google.generativeai.types' has no attribute 'Content'** — Library version was outdated (0.8.3)

## ✅ Solutions Applied

### 1. **Updated Library Version**
- Changed `google-generativeai==0.8.3` → `google-generativeai==0.13.0`
- Install new version:
```bash
pip install -r requirements.txt --upgrade
```

### 2. **Fixed Code Compatibility**
- Updated [services/gemini_service.py](services/gemini_service.py) for the new API
- Added better error messages for debugging

---

## 🔐 Getting a New API Key

### Step 1: Go to Google AI Studio
Visit: **https://aistudio.google.com**

### Step 2: Create an API Key
1. Click **"Get API Key"** (top-left)
2. Select **"Create new secret key in new project"**
3. Copy the generated key

### Step 3: Update Your `.env` File
Edit `d:\7th Semester\Student Mental Health Companion\.env`:

```env
GEMINI_API_KEY=your_new_key_here
SECRET_KEY=sage-super-secret-key-2024-change-in-production
DATABASE_PATH=mental_health.db
DEBUG=True
```

### Step 4: Restart Your App
```bash
python app.py
```
or
```bash
python run.py
```

---

## 🧪 Test If It Works

1. Open your app at `http://localhost:5000`
2. Log in to your account
3. Try sending a chat message
4. If successful, you should see **Feelora's response** (no error messages)

---

## ⚡ Quick Fix Checklist

- [ ] Installed new requirements: `pip install -r requirements.txt --upgrade`
- [ ] Got new API key from https://aistudio.google.com
- [ ] Updated `.env` file with new key
- [ ] Restarted the Flask app
- [ ] Tested chat functionality
- [ ] Tested study plan generation

---

## 🐛 Troubleshooting

### Still seeing "API Key not found"?
- Make sure your `.env` file is in the **root folder** (same level as `app.py`)
- Restart your terminal/IDE completely
- Check the key format (should be a long alphanumeric string starting with "AIza")

### Still seeing "Module has no attribute 'Content'"?
```bash
pip uninstall google-generativeai -y
pip install google-generativeai==0.13.0
```

### API key invalid even after updating?
- Your key might be restricted. Go to https://console.cloud.google.com
- Check that the **Generative Language API** is enabled
- Check quota limits in the API dashboard

---

## 📞 Need Help?

If errors persist, check your app logs:
```bash
# In PowerShell/Terminal, run your app and look for red error messages
python app.py
```

Share the error message with the development team.
