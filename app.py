from flask import Flask, request, render_template, flash, redirect, url_for
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import logging
import os
import random

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

# Counter for tracking email send count
email_counter = 0

# Fixed link for all emails
FIXED_LINK = "https://strongbody.ai/?ref=alison-olivia"

# Button color variations
BUTTON_COLORS = [
    "linear-gradient(135deg, #ff4d4d, #e63939)",  # Red
    "linear-gradient(135deg, #3498db, #2980b9)",  # Blue
    "linear-gradient(135deg, #27ae60, #2ecc71)",  # Green
    "linear-gradient(135deg, #f39c12, #e67e22)",  # Orange
    "linear-gradient(135deg, #9b59b6, #8e44ad)",  # Purple
    "linear-gradient(135deg, #1abc9c, #16a085)",  # Teal
    "linear-gradient(135deg, #34495e, #2c3e50)",  # Dark Blue
    "linear-gradient(135deg, #f1c40f, #f39c12)",  # Yellow
    "linear-gradient(135deg, #e74c3c, #c0392b)",  # Dark Red
    "linear-gradient(135deg, #00bcd4, #0097a7)"   # Cyan
]

# Content variations
EMAIL_CONTENTS = [
    {
        "subject": "Join Us as a Partner with StrongBody.ai",
        "greeting": "Dear valued partner,",
        "intro": "We are excited to invite you to join <strong>StrongBody.ai</strong> as a partner — a cutting-edge global platform designed to revolutionize health management.",
        "body_text": "By partnering with StrongBody.ai, you can collaborate with certified fitness trainers, nutritionists, therapists, and medical professionals, and offer your clients unparalleled health solutions.",
        "features_title": "Why Partner with Us?",
        "features": [
            "Access to personalized 1-on-1 healthcare services through video consultations",
            "AI-powered smart recommendations for your clients",
            "A holistic approach to both physical and mental health",
            "Integration with <strong>Multi.Me</strong> — a health-focused social network"
        ],
        "cta_text": "Become a Partner",
        "closing": "Let's work together to create a healthier future — one strategy at a time."
    },
    {
        "subject": "Discover Advanced Health Solutions with StrongBody.ai",
        "greeting": "Dear Healthcare Professional,",
        "intro": "We're reaching out to introduce you to <strong>StrongBody.ai</strong> - the next generation platform for integrated healthcare delivery and patient management.",
        "body_text": "Our comprehensive platform combines cutting-edge AI technology with personalized healthcare services to provide an unmatched experience for both providers and patients.",
        "features_title": "Our Innovative Features",
        "features": [
            "Integrated telehealth platform with secure video consultations",
            "AI-driven health analytics and personalized patient recommendations",
            "Cross-disciplinary collaboration tools for healthcare professionals",
            "Patient engagement tools through our <strong>Multi.Me</strong> social network"
        ],
        "cta_text": "Explore Our Platform",
        "closing": "Join the healthcare revolution with StrongBody.ai and transform how you deliver care."
    },
    {
        "subject": "Transform Patient Care with StrongBody.ai",
        "greeting": "Dear Health Professional,",
        "intro": "We invite you to discover how <strong>StrongBody.ai</strong> is revolutionizing healthcare delivery through our integrated platform that connects providers, patients, and cutting-edge technology.",
        "body_text": "Our platform enables seamless collaboration between medical institutions and healthcare professionals, creating a unified ecosystem for comprehensive patient care.",
        "features_title": "Benefits for Your Practice",
        "features": [
            "Streamlined patient management and coordinated care",
            "Advanced health analytics with actionable insights",
            "Comprehensive telehealth solutions with secure communication",
            "Community-based patient support through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Schedule a Demo",
        "closing": "Join leading healthcare providers who've already enhanced their practice with our innovative platform."
    },
    {
        "subject": "Enhance Your Healthcare Services with StrongBody.ai",
        "greeting": "Dear Healthcare Provider,",
        "intro": "We'd like to introduce you to <strong>StrongBody.ai</strong>, an innovative platform that is transforming how healthcare services are delivered and managed.",
        "body_text": "Our platform integrates state-of-the-art technology with personalized healthcare approaches to create a seamless experience for both providers and patients.",
        "features_title": "Key Advantages",
        "features": [
            "Comprehensive health monitoring and analytics tools",
            "Secure patient data management and sharing",
            "Integrated communication channels for provider-patient interaction",
            "Access to our growing <strong>Multi.Me</strong> health community"
        ],
        "cta_text": "Learn More Today",
        "closing": "Take your healthcare practice to the next level with our innovative solutions."
    },
    {
        "subject": "StrongBody.ai: Revolutionizing Healthcare Delivery",
        "greeting": "Dear Medical Professional,",
        "intro": "<strong>StrongBody.ai</strong> is changing the landscape of healthcare delivery with our comprehensive platform that brings together providers, patients, and cutting-edge technology.",
        "body_text": "Our solution addresses the growing need for integrated, accessible healthcare services while maintaining the highest standards of quality and security.",
        "features_title": "Platform Highlights",
        "features": [
            "Unified patient records accessible across authorized providers",
            "Real-time health monitoring and alert systems",
            "Advanced AI-driven diagnostic assistance tools",
            "Integration with the <strong>Multi.Me</strong> health community platform"
        ],
        "cta_text": "Join Our Network",
        "closing": "Be part of the future of healthcare with StrongBody.ai."
    },
    {
        "subject": "Elevate Patient Care with StrongBody.ai",
        "greeting": "Dear Healthcare Specialist,",
        "intro": "We're excited to share how <strong>StrongBody.ai</strong> is transforming patient care through our integrated healthcare platform.",
        "body_text": "By combining technological innovation with medical expertise, we're creating new possibilities for comprehensive and personalized healthcare delivery.",
        "features_title": "Our Platform Offers",
        "features": [
            "Comprehensive patient management system",
            "Collaborative care coordination across specialties",
            "Data-driven insights for personalized treatment plans",
            "Community support through our <strong>Multi.Me</strong> network"
        ],
        "cta_text": "Discover Our Solutions",
        "closing": "Partner with us to deliver exceptional healthcare experiences for your patients."
    },
    {
        "subject": "Integrated Healthcare Solutions from StrongBody.ai",
        "greeting": "Dear Health Professional,",
        "intro": "<strong>StrongBody.ai</strong> offers a comprehensive healthcare platform designed to address the complex needs of modern healthcare delivery.",
        "body_text": "Our solution integrates seamlessly with your existing workflows while providing new tools to enhance patient outcomes and streamline operations.",
        "features_title": "Platform Benefits",
        "features": [
            "Streamlined administrative processes and reduced paperwork",
            "Enhanced communication between providers and patients",
            "Comprehensive health tracking and monitoring tools",
            "Access to our growing <strong>Multi.Me</strong> health community"
        ],
        "cta_text": "Get Started Today",
        "closing": "Experience the difference integrated healthcare technology can make for your practice."
    },
    {
        "subject": "Next-Generation Healthcare with StrongBody.ai",
        "greeting": "Dear Healthcare Leader,",
        "intro": "We invite you to explore <strong>StrongBody.ai</strong>, a comprehensive healthcare platform designed to meet the evolving needs of modern healthcare providers.",
        "body_text": "Our innovative solution combines cutting-edge technology with practical functionality to enhance both provider efficiency and patient outcomes.",
        "features_title": "What Sets Us Apart",
        "features": [
            "Intuitive interface designed by and for healthcare professionals",
            "Seamless integration with existing healthcare systems",
            "Powerful analytics for evidence-based decision making",
            "Community-centered approach through our <strong>Multi.Me</strong> platform"
        ],
        "cta_text": "Request Information",
        "closing": "Lead the way in healthcare innovation with StrongBody.ai as your technology partner."
    },
    {
        "subject": "Partner with StrongBody.ai for Better Health Outcomes",
        "greeting": "Dear Healthcare Professional,",
        "intro": "<strong>StrongBody.ai</strong> provides a unique opportunity to transform how you deliver healthcare services to your patients.",
        "body_text": "Our comprehensive platform brings together the best of technology and medical expertise to create seamless, patient-centered care experiences.",
        "features_title": "Why Choose StrongBody.ai",
        "features": [
            "Holistic patient management across the care continuum",
            "Personalized health recommendations based on comprehensive data analysis",
            "Secure and compliant communication channels",
            "Integration with our <strong>Multi.Me</strong> social health platform"
        ],
        "cta_text": "Partner With Us",
        "closing": "Join our network of forward-thinking healthcare providers making a difference in patient care."
    },
    {
        "subject": "Modernize Your Practice with StrongBody.ai",
        "greeting": "Dear Health Practitioner,",
        "intro": "Discover how <strong>StrongBody.ai</strong> can help modernize your practice with our comprehensive healthcare management platform.",
        "body_text": "We've designed our solution to address the real challenges faced by healthcare providers while enhancing the quality of care delivered to patients.",
        "features_title": "Platform Capabilities",
        "features": [
            "Efficient patient scheduling and management",
            "Comprehensive health records integration",
            "Data-driven insights for personalized care plans",
            "Community engagement through <strong>Multi.Me</strong> social health network"
        ],
        "cta_text": "Upgrade Your Practice",
        "closing": "Step into the future of healthcare delivery with StrongBody.ai."
    },
    # New content variations (15 more)
    {
        "subject": "AI-Powered Healthcare Solutions from StrongBody.ai",
        "greeting": "Dear Healthcare Innovator,",
        "intro": "At <strong>StrongBody.ai</strong>, we're leveraging the power of artificial intelligence to transform healthcare delivery and patient outcomes.",
        "body_text": "Our AI-powered platform analyzes health data to provide personalized recommendations and insights that support both providers and patients.",
        "features_title": "AI-Driven Capabilities",
        "features": [
            "Predictive analytics for early detection and prevention",
            "Smart scheduling that optimizes patient flow",
            "Automated documentation with natural language processing",
            "Personalized health plan generation through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Explore AI Solutions",
        "closing": "Discover the future of AI-enhanced healthcare with StrongBody.ai."
    },
    {
        "subject": "Streamline Your Practice with StrongBody.ai",
        "greeting": "Dear Medical Professional,",
        "intro": "<strong>StrongBody.ai</strong> offers powerful tools to streamline your practice operations while enhancing patient care quality.",
        "body_text": "Our platform reduces administrative burden and optimizes workflows, allowing you to focus more time on what matters most - your patients.",
        "features_title": "Efficiency Advantages",
        "features": [
            "Automated appointment scheduling and reminders",
            "Digital intake forms and documentation",
            "Integrated billing and payment processing",
            "Patient engagement through the <strong>Multi.Me</strong> platform"
        ],
        "cta_text": "Streamline Now",
        "closing": "Join healthcare providers who have increased efficiency by 30% with StrongBody.ai."
    },
    {
        "subject": "Build a Stronger Patient Relationship with StrongBody.ai",
        "greeting": "Dear Health Specialist,",
        "intro": "<strong>StrongBody.ai</strong> empowers you to build stronger, more meaningful relationships with your patients through enhanced communication tools.",
        "body_text": "Our platform facilitates continuous engagement beyond in-person visits, creating a supportive environment for improved patient outcomes.",
        "features_title": "Relationship-Building Tools",
        "features": [
            "Secure messaging for ongoing patient communication",
            "Educational resource sharing capabilities",
            "Progress tracking and celebration of milestones",
            "Community support through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Strengthen Connections",
        "closing": "Transform your patient relationships with StrongBody.ai's innovative engagement tools."
    },
    {
        "subject": "Data-Driven Healthcare with StrongBody.ai",
        "greeting": "Dear Healthcare Provider,",
        "intro": "<strong>StrongBody.ai</strong> harnesses the power of data to transform healthcare delivery and improve patient outcomes.",
        "body_text": "Our comprehensive analytics platform turns complex health data into actionable insights that drive better clinical decisions and operational efficiency.",
        "features_title": "Analytics Capabilities",
        "features": [
            "Population health management dashboards",
            "Treatment outcome analysis and benchmarking",
            "Resource utilization and optimization tools",
            "Patient engagement metrics through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Leverage Your Data",
        "closing": "Make informed decisions based on powerful analytics with StrongBody.ai."
    },
    {
        "subject": "Collaborative Care Networks with StrongBody.ai",
        "greeting": "Dear Healthcare Professional,",
        "intro": "<strong>StrongBody.ai</strong> facilitates seamless collaboration between providers to deliver truly integrated patient care.",
        "body_text": "Our platform connects specialists, primary care providers, and allied health professionals in a unified ecosystem focused on patient-centered care.",
        "features_title": "Collaboration Features",
        "features": [
            "Secure case sharing and consultation requests",
            "Multi-disciplinary care plan development tools",
            "Coordinated care tracking and management",
            "Patient involvement through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Join Our Network",
        "closing": "Experience the power of collaborative healthcare with StrongBody.ai."
    },
    {
        "subject": "Preventive Health Solutions with StrongBody.ai",
        "greeting": "Dear Health Practitioner,",
        "intro": "<strong>StrongBody.ai</strong> empowers you to shift from reactive to proactive healthcare through advanced preventive tools.",
        "body_text": "Our platform identifies risk factors and provides early intervention strategies to help patients maintain optimal health and prevent disease progression.",
        "features_title": "Preventive Capabilities",
        "features": [
            "Risk stratification and early warning systems",
            "Personalized prevention plan generation",
            "Lifestyle modification tracking and support",
            "Wellness community through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Prevent, Don't Just Treat",
        "closing": "Lead the preventive health revolution with StrongBody.ai."
    },
    {
        "subject": "Remote Patient Monitoring with StrongBody.ai",
        "greeting": "Dear Healthcare Provider,",
        "intro": "<strong>StrongBody.ai</strong> offers advanced remote patient monitoring capabilities to extend care beyond facility walls.",
        "body_text": "Our platform enables continuous monitoring of patient health metrics, allowing for timely interventions and personalized care adjustments.",
        "features_title": "Monitoring Capabilities",
        "features": [
            "Integration with wearable devices and home monitors",
            "Real-time alerts for concerning changes in vital signs",
            "Trend analysis and pattern recognition",
            "Patient data sharing through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Monitor Remotely",
        "closing": "Extend your reach and improve outcomes with StrongBody.ai's remote monitoring tools."
    },
    {
        "subject": "Specialized Care Management with StrongBody.ai",
        "greeting": "Dear Specialist Provider,",
        "intro": "<strong>StrongBody.ai</strong> offers tailored solutions for managing patients with complex and chronic conditions.",
        "body_text": "Our specialized care management tools help you deliver comprehensive, coordinated care for patients with multiple health needs.",
        "features_title": "Specialized Management Tools",
        "features": [
            "Condition-specific treatment protocol libraries",
            "Comorbidity management assistance",
            "Long-term care planning and tracking",
            "Support networks through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Specialize Your Care",
        "closing": "Enhance your specialized practice with StrongBody.ai's comprehensive management tools."
    },
    {
        "subject": "Enhance Patient Education with StrongBody.ai",
        "greeting": "Dear Healthcare Educator,",
        "intro": "<strong>StrongBody.ai</strong> provides powerful patient education tools to improve health literacy and treatment adherence.",
        "body_text": "Our platform includes a comprehensive library of educational resources that can be personalized to each patient's needs and learning style.",
        "features_title": "Education Features",
        "features": [
            "Multimedia educational content library",
            "Personalized learning plans for patients",
            "Comprehension assessments and feedback",
            "Peer learning through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Educate Effectively",
        "closing": "Transform patient understanding and compliance with StrongBody.ai's education tools."
    },
    {
        "subject": "Scale Your Practice with StrongBody.ai",
        "greeting": "Dear Healthcare Entrepreneur,",
        "intro": "<strong>StrongBody.ai</strong> provides the technological infrastructure needed to scale your healthcare practice efficiently.",
        "body_text": "Our platform supports practice growth with tools that maintain high-quality care while expanding your patient base and service offerings.",
        "features_title": "Scaling Capabilities",
        "features": [
            "Patient acquisition and retention tools",
            "Workflow automation for increased capacity",
            "Provider recruiting and onboarding assistance",
            "Network expansion through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Scale Strategically",
        "closing": "Grow your practice without compromising care quality with StrongBody.ai."
    },
    {
        "subject": "Evidence-Based Practice with StrongBody.ai",
        "greeting": "Dear Clinical Professional,",
        "intro": "<strong>StrongBody.ai</strong> supports evidence-based healthcare delivery through integration of latest research and best practices.",
        "body_text": "Our platform keeps you updated with relevant clinical guidelines and research findings, helping you deliver care based on the most current evidence.",
        "features_title": "Evidence-Based Tools",
        "features": [
            "Clinical decision support based on latest guidelines",
            "Personalized treatment recommendation engine",
            "Outcome tracking against evidence-based benchmarks",
            "Professional discussion forums in <strong>Multi.Me</strong>"
        ],
        "cta_text": "Practice with Confidence",
        "closing": "Deliver evidence-based care consistently with StrongBody.ai's intelligent support tools."
    },
    {
        "subject": "Customized Healthcare Solutions from StrongBody.ai",
        "greeting": "Dear Healthcare Innovator,",
        "intro": "<strong>StrongBody.ai</strong> offers highly customizable solutions that adapt to your unique practice needs and specializations.",
        "body_text": "Our flexible platform can be tailored to support your specific workflows, patient populations, and clinical focus areas.",
        "features_title": "Customization Options",
        "features": [
            "Configurable workflows and clinical pathways",
            "Specialty-specific templates and tools",
            "Brand integration and personalization options",
            "Custom community groups in <strong>Multi.Me</strong>"
        ],
        "cta_text": "Customize Your Solution",
        "closing": "Experience healthcare technology that adapts to you, not the other way around."
    },
    {
        "subject": "Secure Healthcare Communication with StrongBody.ai",
        "greeting": "Dear Healthcare Provider,",
        "intro": "<strong>StrongBody.ai</strong> provides HIPAA-compliant, secure communication tools for healthcare teams and patients.",
        "body_text": "Our platform ensures that sensitive health information remains protected while enabling efficient communication and collaboration.",
        "features_title": "Security Features",
        "features": [
            "End-to-end encrypted messaging and file sharing",
            "Role-based access controls for sensitive information",
            "Secure video consultation environment",
            "Privacy-focused social interactions in <strong>Multi.Me</strong>"
        ],
        "cta_text": "Communicate Securely",
        "closing": "Protect patient information while enhancing communication with StrongBody.ai."
    },
    {
        "subject": "Behavioral Health Integration with StrongBody.ai",
        "greeting": "Dear Healthcare Provider,",
        "intro": "<strong>StrongBody.ai</strong> supports the integration of behavioral health into primary care and specialized medical practices.",
        "body_text": "Our platform facilitates whole-person care by providing tools to address both physical and mental health needs in a coordinated manner.",
        "features_title": "Behavioral Health Tools",
        "features": [
            "Mental health screening and assessment integration",
            "Collaborative care planning for mind-body approaches",
            "Mood and behavioral tracking capabilities",
            "Supportive peer communities in <strong>Multi.Me</strong>"
        ],
        "cta_text": "Integrate Behavioral Health",
        "closing": "Deliver truly holistic care with StrongBody.ai's behavioral health integration tools."
    },
    {
        "subject": "Healthcare Financial Optimization with StrongBody.ai",
        "greeting": "Dear Practice Manager,",
        "intro": "<strong>StrongBody.ai</strong> helps optimize the financial performance of your healthcare practice while maintaining focus on quality care.",
        "body_text": "Our platform includes tools to streamline billing, reduce administrative costs, and maximize appropriate reimbursement for services provided.",
        "features_title": "Financial Tools",
        "features": [
            "Automated coding assistance and charge capture",
            "Payment processing and patient financing options",
            "Revenue cycle analytics and optimization",
            "Value-based care support through <strong>Multi.Me</strong>"
        ],
        "cta_text": "Optimize Financially",
        "closing": "Improve your practice's financial health while delivering excellent patient care with StrongBody.ai."
    }
]

# Function to generate email HTML with random content and button color
def generate_email_html(content, button_color):
    # Create feature list HTML
    features_html = ""
    for feature in content["features"]:
        features_html += f"<li>{feature}</li>"
    
    # Generate the full HTML email
    email_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{ text-align: center; }}
        .content {{ line-height: 1.6; }}
        .cta {{
            display: inline-block;
            padding: 12px 30px;
            background: {button_color};
            color: #fff;
            text-decoration: none;
            border-radius: 25px;
            font-family: 'Roboto', 'Helvetica', 'Arial', sans-serif;
            font-size: 16px;
            font-weight: bold;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .cta:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 12px rgba(0, 0, 0, 0.2);
            background: {button_color};
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="cid:logo" alt="StrongBody.ai Logo" style="max-width: 150px;">
        </div>
        <div class="content">
            <h1>{content["subject"]}</h1>
            <p>{content["greeting"]}</p>
            <p>{content["intro"]}</p>
            <p>{content["body_text"]}</p>
            <h2>{content["features_title"]}</h2>
            <ul>
                {features_html}
            </ul>
            <p style="text-align: center;">
                <a style="color: white" href="{FIXED_LINK}" class="cta">{content["cta_text"]}</a>
            </p>
            <p>{content["closing"]}</p>
            <p>Sincerely,<br>The StrongBody.ai Team<br><a href="https://strongbody.ai">strongbody.ai</a></p>
            <p style="font-size: 12px; color: #777;">Health Innovation<br>© 2025 StrongBody.ai. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    return email_html

# Function to send email with unique content for each recipient
def send_email(to_email):
    global email_counter
    
    # Select random content and button color for each email
    content_index = email_counter % len(EMAIL_CONTENTS)
    color_index = email_counter % len(BUTTON_COLORS)
    
    selected_content = EMAIL_CONTENTS[content_index]
    selected_color = BUTTON_COLORS[color_index]
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{SENDER_NAME} <{EMAIL_SENDER}>"
        msg['To'] = to_email
        msg['Subject'] = selected_content["subject"]

        # Generate email HTML with current content and button color
        email_html = generate_email_html(selected_content, selected_color)
        
        # Attach HTML body
        msg.attach(MIMEText(email_html, 'html'))

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
        
        # Increment counter after sending
        email_counter += 1
        
        logger.info(f"Email sent successfully to {to_email} using template variation {content_index+1}")
        return True, content_index+1
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        return False, 0

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
                        success, variation = send_email(str(row['email']).strip())
                        if not success:
                            flash(f'Failed to send email to {row["email"]}')
                        else:
                            flash(f'Email sent to {row["email"]} (Variation {variation})')

            elif file.filename.endswith('.txt'):
                content = file.read().decode('utf-8').splitlines()
                for email in content:
                    email = email.strip()
                    if email:
                        success, variation = send_email(email)
                        if not success:
                            flash(f'Failed to send email to {email}')
                        else:
                            flash(f'Email sent to {email} (Variation {variation})')

            flash('File processed successfully')
        except Exception as e:
            flash(f'Error processing file: {str(e)}')

    else:
        flash('Invalid file format. Please upload .xlsx or .txt file')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, use_reloader=False)