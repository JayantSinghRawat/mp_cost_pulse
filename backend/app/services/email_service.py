import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailService:
    @staticmethod
    def send_otp_email(to_email: str, otp_code: str) -> bool:
        """Send OTP code to user's email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = "Your Login Verification Code"
            
            # Email body
            body = f"""
            <html>
              <body>
                <h2>Two-Factor Authentication</h2>
                <p>Your verification code is:</p>
                <h1 style="color: #667eea; font-size: 32px; letter-spacing: 5px;">{otp_code}</h1>
                <p>This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

