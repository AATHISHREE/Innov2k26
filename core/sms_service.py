"""
core/sms_service.py - SMS alert service
"""

import os
from dotenv import load_dotenv
import random

load_dotenv()

class SMSService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.clinic_number = os.getenv('CLINIC_PHONE_NUMBER')
        
        # Initialize Twilio if credentials exist
        if self.account_sid and self.auth_token:
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
            except:
                self.client = None
                print("⚠️ Twilio not installed. Using mock mode.")
        else:
            self.client = None
            print("⚠️ Twilio credentials not found. Using mock SMS mode.")
    
    def send_alert(self, patient_name, risk_level, confidence, patient_id, location=""):
        """Send SMS alert"""
        message = f"""🚨 PULSEECHO HEART ALERT

High-risk heart murmur detected!

Patient: {patient_name}
ID: {patient_id}
Risk Level: {risk_level}
Confidence: {confidence}%

Location: {location if location else 'Not specified'}

Immediate pediatric cardiology consult recommended.

This is an automated alert from PulseEcho System."""

        try:
            if self.client and self.clinic_number:
                # Send real SMS
                twilio_message = self.client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=self.clinic_number
                )
                
                return {
                    "success": True,
                    "message_id": twilio_message.sid,
                    "to": self.clinic_number,
                    "message": "SMS alert sent successfully"
                }
            else:
                # Mock SMS for demo
                print(f"📱 [DEMO SMS]: {message[:100]}...")
                return {
                    "success": True,
                    "message_id": f"mock_{random.randint(1000, 9999)}",
                    "to": "+1234567890 (Mock)",
                    "message": "Mock SMS sent for demo"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to send SMS alert"
            }

# Global instance
sms_service = SMSService()

def send_alert_sms(patient_name, risk_level, confidence, patient_id, location=""):
    """Public interface for SMS alerts"""
    return sms_service.send_alert(patient_name, risk_level, confidence, patient_id, location)

if __name__ == "__main__":
    # Test
    result = send_alert_sms(
        patient_name="Test Patient",
        risk_level="HIGH",
        confidence=95,
        patient_id="test_001",
        location="Cardiology Clinic"
    )
    print(f"SMS Test: {result['success']} - {result.get('message')}")