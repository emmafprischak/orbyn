# Nova Voice Agent

**AI-Powered Voice Agent for Orbyn.ai**

Nova is an intelligent voice agent that handles phone calls, books appointments, sends SMS confirmations, and logs leads to your CRM - all automatically.

## Features

- **Natural Conversations**: Powered by OpenAI GPT-4 for human-like interactions
- **Appointment Booking**: Integrates with Cal.com to check availability and schedule consultations
- **SMS Confirmations**: Automatically sends appointment confirmations via Twilio
- **CRM Integration**: Logs all leads and appointments to Notion database
- **Smart Fallbacks**: Continues working even if external APIs fail

## Phone Number

**Call Nova**: +1 (814) 568-5796

## Technology Stack

- **Backend**: FastAPI 0.104.1
- **Python**: 3.10+
- **Telephony**: Twilio Voice API
- **AI**: OpenAI GPT-4
- **Scheduling**: Cal.com API
- **CRM**: Notion API
- **SMS**: Twilio SMS API

## Project Structure

```
nova-voice-agent/
├── .env                    # API credentials
├── .gitignore
├── requirements.txt
├── README.md
└── backend/
    ├── main.py            # FastAPI entry point
    ├── config.py          # Configuration
    ├── models.py          # Data models
    ├── routes/
    │   ├── health.py      # Health checks
    │   └── webhooks.py    # Twilio webhooks
    └── services/
        ├── conversation.py # OpenAI integration
        ├── calendar.py     # Cal.com integration
        ├── sms.py         # Twilio SMS
        └── crm.py         # Notion integration
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- ngrok (for local development)

### Installation

1. **Clone or navigate to the project:**
   ```bash
   cd nova-voice-agent
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify .env file:**
   The `.env` file is already configured with your API credentials. Make sure it exists in the root directory.

### Running the Server

1. **Start the FastAPI server:**
   ```bash
   cd backend
   python main.py
   ```

   You should see:
   ```
   ============================================================
   🚀 Nova Voice Agent Starting...
   ============================================================
   📱 Phone Number: +1 (814) 568-5796
   🌐 Server: http://0.0.0.0:8000
   📝 Health Check: http://0.0.0.0:8000/health
   🔗 Webhooks: http://0.0.0.0:8000/webhooks/voice/incoming
   ============================================================
   ✅ Ready to receive calls!
   ============================================================
   ```

2. **Test the health endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

### Setting Up ngrok (For Local Development)

To allow Twilio to reach your local server, use ngrok:

1. **Install ngrok:**
   - Download from https://ngrok.com/download
   - Or use: `brew install ngrok` (macOS) or `snap install ngrok` (Linux)

2. **Start ngrok tunnel:**
   ```bash
   ngrok http 8000
   ```

3. **Copy the forwarding URL:**
   ```
   Forwarding: https://abc123.ngrok.io -> http://localhost:8000
   ```

4. **Configure Twilio webhook:**
   - Go to https://console.twilio.com/
   - Navigate to Phone Numbers > Manage > Active Numbers
   - Click on your phone number: +1 (814) 568-5796
   - Under "Voice Configuration":
     - Set "A CALL COMES IN" to: `https://abc123.ngrok.io/webhooks/voice/incoming`
     - Set "METHOD" to: POST
   - Under "Status Callback":
     - Set URL to: `https://abc123.ngrok.io/webhooks/voice/status`
   - Click Save

### Testing Nova

1. **Call the phone number:**
   ```
   +1 (814) 568-5796
   ```

2. **Have a conversation:**
   - Nova: "Hi! This is Nova from Orbyn dot A I. Thanks for calling! How can I help you today?"
   - You: "I'd like to schedule a consultation"
   - Nova: "Great! What's your name?"
   - You: "John Doe"
   - Nova: "Thanks John! What's the best phone number to reach you?"
   - You: "555-123-4567"
   - Nova: "What service are you interested in?"
   - You: "AI consulting"
   - Nova: "Would you like to schedule a free consultation?"
   - You: "Yes"
   - Nova: "I have openings on Friday at 10 AM, 2 PM, or Monday at 10 AM. Which time works best?"
   - You: "Friday at 10 AM"
   - Nova: "Perfect! I've scheduled your consultation. Check your phone for confirmation. Goodbye!"

3. **Check the results:**
   - You should receive an SMS confirmation
   - Check your Notion database for the new lead entry
   - Check Cal.com for the booked appointment (or pending status)

## API Endpoints

### Health Checks
- `GET /` - API information
- `GET /health` - Health status

### Twilio Webhooks
- `POST /webhooks/voice/incoming` - Handle incoming calls
- `POST /webhooks/voice/process` - Process user speech
- `POST /webhooks/voice/book` - Book appointments
- `POST /webhooks/voice/status` - Call status updates

## Conversation Flow

1. **Greeting** - Nova introduces herself
2. **Information Collection** - Asks for name, phone, service interest
3. **Confirmation** - Repeats information back
4. **Booking Offer** - Asks if customer wants to schedule
5. **Slot Presentation** - Shows available appointment times
6. **Booking Confirmation** - Books appointment, sends SMS, logs to Notion
7. **Call End** - Thanks customer and hangs up

## Configuration

### Environment Variables

All configuration is in `.env`:

```env
# Twilio
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# OpenAI
OPENAI_API_KEY=...

# Cal.com
CAL_API_KEY=...
CAL_EVENT_TYPE=...

# Notion
NOTION_TOKEN=...
NOTION_DATABASE_ID=...

# Server
HOST=0.0.0.0
PORT=8000
```

### Nova's Personality

Nova's personality is defined in `backend/config.py`:
- Friendly and professional
- Keeps responses under 3 sentences (phone-appropriate)
- Confirms information by repeating it back
- Focuses on booking consultations

## Error Handling

Nova is built with robust error handling:

- **Cal.com failures**: Uses fallback appointment slots
- **Notion failures**: Logs error but continues (doesn't crash calls)
- **OpenAI failures**: Returns friendly error message to caller
- **SMS failures**: Logs error but booking still succeeds

All errors are logged to console with emoji indicators for easy debugging.

## Debugging

The system uses emoji-prefixed logging for easy monitoring:

- 📞 Call events
- 🗣️ User speech
- 🤖 AI responses
- 📊 Extracted data
- 📅 Calendar operations
- 📱 SMS operations
- 📝 Notion operations
- ✅ Success indicators
- ❌ Error indicators

Watch the console output while testing to see the full conversation flow.

## Notion Database Schema

Your Notion database should have these properties:

- **name** (title) - Customer name
- **phone_number** (rich text) - Phone number
- **email** (rich text) - Email address
- **service** (rich text) - Service interest
- **status** (select/rich text) - Lead status (new, qualified, booked, needs_callback, no_booking)
- **date** (date) - Appointment date/time
- **notes** (rich text) - Additional notes and Call SID

## Production Deployment

For production deployment:

1. **Remove reload mode:**
   - Edit `backend/main.py`
   - Change `reload=True` to `reload=False`

2. **Use a production server:**
   - Deploy to Heroku, AWS, Google Cloud, or similar
   - Ensure server has public HTTPS URL

3. **Update Twilio webhooks:**
   - Point to production URL instead of ngrok

4. **Secure your .env:**
   - Never commit `.env` to git
   - Use environment variable management in production

## Troubleshooting

### Server won't start
- Check Python version: `python --version` (need 3.10+)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check if port 8000 is available

### Twilio can't reach webhooks
- Verify ngrok is running: `ngrok http 8000`
- Check Twilio webhook configuration matches ngrok URL
- Ensure ngrok URL uses HTTPS

### OpenAI errors
- Verify API key is correct in `.env`
- Check OpenAI account has credits

### Cal.com booking fails
- Check API key and event type in `.env`
- Verify Cal.com account is active
- System will use fallback and mark as "pending"

### Notion integration fails
- Verify database ID and token in `.env`
- Check database properties match schema
- System will continue without failing call

## Development

### Adding New Features

1. **New service** - Add to `backend/services/`
2. **New route** - Add to `backend/routes/`
3. **New model** - Add to `backend/models.py`
4. **Update config** - Edit `backend/config.py`

### Code Style

- Use async/await for I/O operations
- Add type hints to function signatures
- Include docstrings for functions
- Use emoji logging for consistency

## Support

For issues or questions:
1. Check console logs for error messages
2. Verify all API credentials are correct
3. Test each service individually
4. Review Twilio webhook logs in Twilio console

## License

This project is for educational purposes as part of a senior design project.

## Credits

Built for Orbyn.ai by Emma Prischak
Senior Design Project 2025
