import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = {"GMail" : ('smtp.gmail.com', 587)}

def sendEmail(email_address:str, email_recipient:str,
              email_app_password:str, message:str, subject:str,
              mail_service:str="GMail"):

    server = smtplib.SMTP(*SMTP_SERVER[mail_service]) # Replace with your SMTP server and port
    server.starttls() # Encrypt the connection
    server.login(email_address, email_app_password) # Replace with your credentials

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = email_recipient

    server.sendmail(email_address, email_recipient, msg.as_string())

    server.quit()

