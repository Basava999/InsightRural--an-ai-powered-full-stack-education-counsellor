# WhatsApp Bot Integration for InsightRural
# Uses Twilio API for WhatsApp Business messaging

import re
import json
from typing import Optional, Dict, Any

# Twilio imports (optional - gracefully handle if not installed)
try:
    from twilio.rest import Client
    from twilio.twiml.messaging_response import MessagingResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("Warning: Twilio not installed. Run: pip install twilio")


class WhatsAppBot:
    """WhatsApp Bot for InsightRural college guidance."""
    
    # Command patterns
    PATTERNS = {
        'predict': r'(?:predict|college|rank)\s*[:=]?\s*(\d+)',
        'category': r'(?:cat|category)\s*[:=]?\s*(gm|obc|sc|st)',
        'branch': r'(?:branch|course)\s*[:=]?\s*(cse|ece|eee|me|civil|ise|ai|ds)',
        'help': r'^(help|start|hi|hello|menu)$',
        'scholarship': r'scholarship|vidyasiri|post.?matric',
        'loan': r'loan|education\s*loan|student\s*loan',
    }
    
    # Quick responses
    RESPONSES = {
        'welcome': """🎓 *Welcome to InsightRural!*
        
I'm your AI-powered educational guidance assistant for Karnataka engineering students.

*Available Commands:*
📊 *Predict*: Send your KCET rank to get college predictions
   Example: `Rank 5000 GM CSE`

💰 *Scholarships*: Ask about available scholarships
   Example: `scholarship for OBC`

🏦 *Loans*: Get education loan information
   Example: `education loan`

🏫 *Hostels*: Find hostel information
   Example: `hostels in Bangalore`

Type *help* anytime to see this menu again.""",

        'predict_help': """📊 *College Prediction*

To get your college predictions, send your details in this format:

`Rank [YOUR_RANK] [CATEGORY] [BRANCH]`

*Example:* `Rank 5000 GM CSE`

*Categories:* GM, OBC, SC, ST
*Branches:* CSE, ECE, EEE, ME, CIVIL, ISE, AI, DS

I'll show you the best colleges for your rank! 🎯""",

        'scholarship_info': """💰 *Scholarships for Karnataka Students*

1. *Vidyasiri Scholarship*
   - For OBC/SC/ST students
   - Up to ₹50,000/year
   - Apply on SSP Karnataka portal

2. *Post-Matric Scholarship*
   - For SC/ST students
   - Full fee coverage
   - Annual renewal required

3. *NSP (National Scholarship Portal)*
   - Merit-cum-means scholarships
   - Various central schemes
   - Apply at scholarships.gov.in

_Type your category (GM/OBC/SC/ST) for specific scholarships._""",

        'loan_info': """🏦 *Education Loan Options*

1. *SBI Scholar Loan*
   - Up to ₹20 lakhs
   - 8.1% interest rate
   - No collateral up to ₹7.5 lakhs

2. *Vidyalakshmi Portal*
   - Compare loans from 38 banks
   - Single application
   - www.vidyalakshmi.co.in

3. *Karnataka Minority Loan*
   - For minority students
   - Subsidized interest rates
   - Apply through e-Suvidha portal

_Visit your nearest bank for loan application._""",

        'error': """❌ Sorry, I couldn't understand that.

Try these examples:
• `Rank 5000 GM CSE`
• `scholarship`
• `education loan`
• `help`"""
    }

    def __init__(self, account_sid: str = None, auth_token: str = None, predictor=None):
        """
        Initialize WhatsApp bot.
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            predictor: ML predictor instance (optional)
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.predictor = predictor
        self.client = None
        
        if TWILIO_AVAILABLE and account_sid and auth_token:
            self.client = Client(account_sid, auth_token)

    def process_message(self, message: str, from_number: str = None) -> str:
        """
        Process incoming WhatsApp message and return response.
        
        Args:
            message: Incoming message text
            from_number: Sender's phone number (for tracking)
            
        Returns:
            Response message string
        """
        message = message.strip().lower()
        
        # Check for help/greeting
        if re.match(self.PATTERNS['help'], message, re.I):
            return self.RESPONSES['welcome']
        
        # Check for scholarship query
        if re.search(self.PATTERNS['scholarship'], message, re.I):
            return self.RESPONSES['scholarship_info']
        
        # Check for loan query
        if re.search(self.PATTERNS['loan'], message, re.I):
            return self.RESPONSES['loan_info']
        
        # Check for prediction request
        rank_match = re.search(self.PATTERNS['predict'], message, re.I)
        if rank_match:
            return self._handle_prediction(message, rank_match)
        
        # Default response
        return self.RESPONSES['error']

    def _handle_prediction(self, message: str, rank_match) -> str:
        """Handle college prediction request."""
        rank = int(rank_match.group(1))
        
        # Extract category
        category = 'GM'  # Default
        cat_match = re.search(self.PATTERNS['category'], message, re.I)
        if cat_match:
            category = cat_match.group(1).upper()
        
        # Extract branch
        branch = 'CSE'  # Default
        branch_match = re.search(self.PATTERNS['branch'], message, re.I)
        if branch_match:
            branch = branch_match.group(1).upper()
        
        # If predictor is available, use it
        if self.predictor:
            try:
                result = self.predictor.predict(
                    kcet_rank=rank,
                    category=category,
                    preferred_branches=[branch],
                    top_n=5
                )
                return self._format_prediction_result(result, rank, category, branch)
            except Exception as e:
                return f"❌ Prediction error: {str(e)}"
        
        # Fallback response without predictor
        return self._fallback_prediction(rank, category, branch)

    def _format_prediction_result(self, result: Dict, rank: int, category: str, branch: str) -> str:
        """Format ML prediction result for WhatsApp."""
        predictions = result.get('predictions', [])[:5]
        
        if not predictions:
            return f"""📊 *No colleges found for Rank {rank}*
            
Try applying with a higher rank cutoff or consider other branches."""

        response = f"""🎯 *College Predictions*
        
📊 *Rank:* {rank}
🏷️ *Category:* {category}
📚 *Branch:* {branch}

*Top 5 Recommended Colleges:*

"""
        for i, pred in enumerate(predictions, 1):
            probability = pred.get('probability', 0)
            emoji = '🟢' if probability >= 80 else ('🟡' if probability >= 50 else '🔴')
            
            response += f"""{emoji} *{i}. {pred.get('college_name', 'Unknown')}*
   📍 {pred.get('location', 'N/A')}
   💰 Fee: ₹{pred.get('annual_fee', 'N/A'):,}/year
   📈 Chance: {probability}% ({pred.get('category', 'N/A')})

"""
        
        guidance = result.get('counselling_guidance', {})
        if guidance.get('strategy'):
            response += f"💡 *Tip:* {guidance['strategy']}"
        
        return response

    def _fallback_prediction(self, rank: int, category: str, branch: str) -> str:
        """Provide fallback prediction without ML model."""
        # Simple tier-based prediction
        if rank <= 1000:
            tier = "Top government colleges (RVCE, BMSCE, MSRIT)"
            chance = "High"
        elif rank <= 5000:
            tier = "Good private colleges (PESIT, NMIT, AIT)"
            chance = "Good"
        elif rank <= 15000:
            tier = "Mid-tier private colleges (CMR, NHCE, SJCE)"
            chance = "Moderate"
        elif rank <= 50000:
            tier = "Various private colleges available"
            chance = "Many options"
        else:
            tier = "Consider management quota or diploma lateral entry"
            chance = "Limited"

        return f"""📊 *Quick Prediction*

📈 *Rank:* {rank}
🏷️ *Category:* {category}
📚 *Branch:* {branch}

*Expected Tier:* {tier}
*Admission Chance:* {chance}

_For detailed predictions with specific colleges, use our web app at insightrural.com_

💡 *Tip:* Consider multiple branches for more options. Type `help` for more commands."""

    def create_twiml_response(self, message: str) -> str:
        """
        Create TwiML response for Twilio webhook.
        
        Args:
            message: Response message
            
        Returns:
            TwiML XML string
        """
        if TWILIO_AVAILABLE:
            resp = MessagingResponse()
            resp.message(message)
            return str(resp)
        else:
            # Fallback XML without Twilio
            return f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{message}</Message>
</Response>'''

    def send_message(self, to: str, message: str, from_number: str = None) -> bool:
        """
        Send WhatsApp message via Twilio.
        
        Args:
            to: Recipient phone number (with country code)
            message: Message to send
            from_number: Sender WhatsApp number (optional)
            
        Returns:
            True if sent successfully
        """
        if not self.client:
            print("Twilio client not initialized")
            return False
        
        try:
            self.client.messages.create(
                body=message,
                from_=from_number or 'whatsapp:+14155238886',  # Twilio sandbox number
                to=f'whatsapp:{to}'
            )
            return True
        except Exception as e:
            print(f"Failed to send WhatsApp message: {e}")
            return False


# Singleton instance
_bot_instance = None


def get_whatsapp_bot(predictor=None) -> WhatsAppBot:
    """Get singleton WhatsApp bot instance."""
    global _bot_instance
    if _bot_instance is None:
        import os
        _bot_instance = WhatsAppBot(
            account_sid=os.environ.get('TWILIO_ACCOUNT_SID'),
            auth_token=os.environ.get('TWILIO_AUTH_TOKEN'),
            predictor=predictor
        )
    return _bot_instance


# Test the bot
if __name__ == "__main__":
    bot = WhatsAppBot()
    
    # Test messages
    test_messages = [
        "hello",
        "rank 5000 gm cse",
        "scholarship for sc students",
        "education loan",
        "predict 12000 OBC ECE",
        "help"
    ]
    
    print("=" * 50)
    print("WhatsApp Bot Test")
    print("=" * 50)
    
    for msg in test_messages:
        print(f"\n📱 User: {msg}")
        print(f"🤖 Bot: {bot.process_message(msg)}")
        print("-" * 50)
