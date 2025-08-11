import smtplib
from email.mime.text import MIMEText

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "iconmikky112@gmail.com"
SMTP_PASSWORD = "gjntrzjltwheoncz"  # Your Google App Password
SMTP_FROM_EMAIL = "iconmikky112@gmail.com"
TO_EMAIL = "iconmikky112@gmail.com"  # Can be same as sender for testing

# Email content
subject = "SMTP Test Email"
body = "Hello! This is a test email to confirm SMTP works."

# Create MIMEText object
msg = MIMEText(body)
msg["Subject"] = subject
msg["From"] = SMTP_FROM_EMAIL
msg["To"] = TO_EMAIL

try:
    print("Connecting to server...")
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()  # Upgrade connection to secure
    print("Logging in...")
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    print("Sending email...")
    server.sendmail(SMTP_FROM_EMAIL, [TO_EMAIL], msg.as_string())
    print("✅ Email sent successfully!")
    server.quit()
except Exception as e:
    print("❌ Email failed to send.")
    print("Error:", e)
