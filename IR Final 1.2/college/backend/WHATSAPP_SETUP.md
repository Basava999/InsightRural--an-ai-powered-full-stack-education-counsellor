# WhatsApp Bot Setup Guide

## Overview
InsightRural includes a WhatsApp bot that allows students to query college predictions, scholarships, and loans via WhatsApp using Twilio.

## Setup Steps

### 1. Create Twilio Account
1. Go to [twilio.com](https://www.twilio.com/) and sign up (free tier available)
2. Get your **Account SID** and **Auth Token** from the Twilio Console

### 2. Enable WhatsApp Sandbox
1. In Twilio Console, go to **Messaging → Try It Out → WhatsApp**
2. Follow instructions to join the sandbox (send a WhatsApp message to the provided number)
3. Save the sandbox number for testing

### 3. Configure Environment Variables
Create a `.env` file in the backend folder:

```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
```

### 4. Configure Webhook URL
1. In Twilio Console, go to **WhatsApp Sandbox Settings**
2. Set the webhook URL:
   - **When a message comes in**: `https://your-domain.com/api/whatsapp/webhook`
   - Method: `POST`

### 5. For Local Testing (Using ngrok)
```bash
# Install ngrok
npm install -g ngrok

# Start your Flask server
python app.py

# In another terminal, expose your local server
ngrok http 5000

# Use the ngrok URL in Twilio webhook settings
# Example: https://abc123.ngrok.io/api/whatsapp/webhook
```

## Testing Without Twilio

You can test the bot logic without Twilio using the test endpoint:

```bash
# Test using curl
curl -X POST http://localhost:5000/api/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'

# Test prediction
curl -X POST http://localhost:5000/api/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{"message": "rank 5000 gm cse"}'
```

## Available Commands

| Command | Description |
|---------|-------------|
| `hello` / `help` | Show welcome message and menu |
| `rank 5000 GM CSE` | Get college predictions for KCET rank |
| `scholarship` | Get scholarship information |
| `education loan` | Get education loan options |

## Production Deployment

For production:
1. Use a proper WSGI server (gunicorn)
2. Set up HTTPS (required by Twilio)
3. Use environment variables for sensitive data
4. Consider rate limiting for the webhook endpoint

## Troubleshooting

- **Messages not reaching**: Check webhook URL is correct and accessible
- **Bot not responding**: Check Flask logs for errors
- **Prediction errors**: Ensure ML predictor is loaded correctly
