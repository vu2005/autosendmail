from flask import Flask, request, render_template, flash, redirect, url_for
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'a1b2c3d4e5f6g7h8i9j0k1l2'  # Replace with a random string
logger.info("Starting Flask application...")

# Gmail credentials
EMAIL_SENDER = 'health.strongsbody@gmail.com'
PASSWORD = 'mowu ekwk ppvq myww'  # App password
SENDER_NAME = "StrongBody"

# Email template
EMAIL_SUBJECT = "Join Us as a Partner with StrongBody.ai"
EMAIL_BODY = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { text-align: center; }
        .content { line-height: 1.6; }
        .cta {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #ff4d4d, #e63939);
            color: #fff;
            text-decoration: none;
            border-radius: 25px;
            font-family: 'Roboto', 'Helvetica', 'Arial', sans-serif;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .cta:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 12px rgba(0, 0, 0, 0.2);
            background: linear-gradient(135deg, #e63939, #cc3333);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="cid:logo" alt="StrongBody.ai Logo" style="max-width: 150px;">
        </div>
        <div class="content">
            <h1>Join Us as a Partner with StrongBody.ai</h1>
            <p>Dear valued partner,</p>
            <p>We are excited to invite you to join <strong>StrongBody.ai</strong> as a partner — a cutting-edge global platform designed to revolutionize health management.</p>
            <p>By partnering with StrongBody.ai, you can collaborate with certified fitness trainers, nutritionists, therapists, and medical professionals, and offer your clients unparalleled health solutions.</p>
            <h2>Why Partner with Us?</h2>
            <ul>
                <li>Access to personalized 1-on-1 healthcare services through video consultations</li>
                <li>AI-powered smart recommendations for your clients</li>
                <li>A holistic approach to both physical and mental health</li>
                <li>Integration with <strong>Multi.Me</strong> — a health-focused social network</li>
            </ul>
            <p style="text-align: center;">
                <a style="color: white" href="https://strongbody.ai/?ref=stronghealth" class="cta">Become a Partner</a>
            </p>
            <p>Let’s work together to create a healthier future — one strategy at a time.</p>
            <p>Sincerely,<br>The StrongBody.ai Team<br><a href="https://strongbody.ai">strongbody.ai</a></p>
            <p style="font-size: 12px; color: #777;">Health Banner<br>© 2025 StrongBody.ai. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""

# Function to send email
def send_email(to_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{SENDER_NAME} <{EMAIL_SENDER}>"
        msg['To'] = to_email
        msg['Subject'] = EMAIL_SUBJECT

        # Attach HTML body
        msg.attach(MIMEText(EMAIL_BODY, 'html'))

        # Attach logo image
        logo_path = os.path.join(os.getcwd(), 'logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as img_file:
                img = MIMEImage(img_file.read())
                img.add_header('Content-ID', '<logo>')
                img.add_header('Content-Disposition', 'inline', filename='logo.png')
                msg.attach(img)
        else:
            logger.warning(f"Logo file not found at {logo_path}")

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file uploaded')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))

    if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.txt')):
        try:
            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
                if 'email' not in df.columns:
                    flash('Excel file must contain "email" column')
                    return redirect(url_for('index'))

                for _, row in df.iterrows():
                    if pd.notna(row['email']):
                        success = send_email(str(row['email']).strip())
                        if not success:
                            flash(f'Failed to send email to {row["email"]}')
                        else:
                            flash(f'Email sent to {row["email"]}')

            elif file.filename.endswith('.txt'):
                content = file.read().decode('utf-8').splitlines()
                for email in content:
                    email = email.strip()
                    if email:
                        success = send_email(email)
                        if not success:
                            flash(f'Failed to send email to {email}')
                        else:
                            flash(f'Email sent to {email}')

            flash('File processed successfully')
        except Exception as e:
            flash(f'Error processing file: {str(e)}')

    else:
        flash('Invalid file format. Please upload .xlsx or .txt file')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, use_reloader=False)