"""
SMS OTP Service for SRM Chatbot Authentication
Uses Twilio for real SMS sending
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import random
import time
from typing import Dict, Optional
import os

# You'll need to install: pip install twilio
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️  Twilio not installed. Install with: pip install twilio")

router = APIRouter()

# In-memory OTP storage (use Redis in production)
otp_store: Dict[str, dict] = {}

# Twilio configuration (GET FREE TRIAL: https://www.twilio.com/try-twilio)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'YOUR_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'YOUR_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+1234567890')  # Your Twilio number

if TWILIO_AVAILABLE:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✅ Twilio SMS service initialized")
    except:
        twilio_client = None
        print("⚠️  Twilio credentials not configured")
else:
    twilio_client = None


class SendOTPRequest(BaseModel):
    phone: str
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str


def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_sms_twilio(phone: str, otp: str) -> bool:
    """Send OTP via Twilio SMS"""
    if not twilio_client:
        return False
    
    try:
        # Add +91 for Indian numbers if not present
        if not phone.startswith('+'):
            phone = f'+91{phone}'
        
        message = twilio_client.messages.create(
            body=f'Your SRM Chatbot OTP is: {otp}\n\nValid for 5 minutes.\n\n- Kivy, SRM Assistant',
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )
        
        print(f"✅ SMS sent to {phone}: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ SMS failed: {str(e)}")
        return False


@router.post("/auth/send-otp")
async def send_otp(request: SendOTPRequest):
    """
    Send OTP to user's phone
    
    FREE TRIAL: Get Twilio account at https://www.twilio.com/try-twilio
    - $15 free credit
    - Can send to verified numbers
    """
    phone = request.phone.strip()
    
    # Validate Indian phone number
    if not phone.isdigit() or len(phone) != 10:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    
    if not phone.startswith(('6', '7', '8', '9')):
        raise HTTPException(status_code=400, detail="Phone must start with 6-9")
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP with expiry (5 minutes)
    otp_store[phone] = {
        'otp': otp,
        'email': request.email,
        'timestamp': time.time(),
        'attempts': 0
    }
    
    # Send SMS
    if TWILIO_AVAILABLE and twilio_client:
        sms_sent = send_sms_twilio(phone, otp)
        
        if sms_sent:
            return {
                'success': True,
                'message': f'OTP sent to {phone}',
                'method': 'sms',
                'expires_in': 300  # 5 minutes
            }
        else:
            # Fallback: return OTP in response (DEV MODE ONLY!)
            return {
                'success': True,
                'message': 'SMS service unavailable. Using dev mode.',
                'method': 'dev',
                'otp': otp,  # REMOVE IN PRODUCTION!
                'expires_in': 300
            }
    else:
        # Development mode - return OTP directly
        return {
            'success': True,
            'message': 'Development mode: OTP generated',
            'method': 'dev',
            'otp': otp,  # REMOVE IN PRODUCTION!
            'expires_in': 300
        }


@router.post("/auth/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    """Verify OTP entered by user"""
    phone = request.phone.strip()
    otp = request.otp.strip()
    
    # Check if OTP exists
    if phone not in otp_store:
        raise HTTPException(status_code=400, detail="No OTP found. Please request new OTP.")
    
    stored = otp_store[phone]
    
    # Check expiry (5 minutes)
    if time.time() - stored['timestamp'] > 300:
        del otp_store[phone]
        raise HTTPException(status_code=400, detail="OTP expired. Please request new OTP.")
    
    # Check attempts (max 3)
    if stored['attempts'] >= 3:
        del otp_store[phone]
        raise HTTPException(status_code=400, detail="Too many attempts. Please request new OTP.")
    
    # Verify OTP
    if otp == stored['otp']:
        # Success! Clean up
        email = stored['email']
        del otp_store[phone]
        
        return {
            'success': True,
            'message': 'OTP verified successfully',
            'email': email,
            'phone': phone,
            'authenticated': True
        }
    else:
        # Increment attempts
        stored['attempts'] += 1
        remaining = 3 - stored['attempts']
        
        return {
            'success': False,
            'message': f'Incorrect OTP. {remaining} attempts remaining.',
            'authenticated': False
        }


@router.post("/auth/resend-otp")
async def resend_otp(phone: str):
    """Resend OTP to phone"""
    phone = phone.strip()
    
    if phone not in otp_store:
        raise HTTPException(status_code=400, detail="No active session. Please start over.")
    
    # Get email from previous request
    email = otp_store[phone]['email']
    
    # Resend
    return await send_otp(SendOTPRequest(phone=phone, email=email))