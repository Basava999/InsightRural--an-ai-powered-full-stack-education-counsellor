# InsightRural Backend Deployment

## Quick Setup

### 1. Get Groq API Key (FREE)
1. Go to https://console.groq.com/keys
2. Sign up with Google/GitHub
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)

### 2. Run Locally
```powershell
cd backend
$env:GROQ_API_KEY = "your_key_here"
python app.py
```

### 3. Deploy to Render (FREE)

1. Push code to GitHub
2. Go to https://render.com
3. Create new "Web Service"
4. Connect your GitHub repo
5. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
6. Add Environment Variable:
   - Key: `GROQ_API_KEY`
   - Value: your API key

Your app will be live at `https://your-app.onrender.com`

### API Endpoints
- `GET /api/health` - Health check
- `GET /api/ai/status` - AI status
- `POST /api/chat` - Chat with AI
- `GET /api/colleges` - Get colleges
