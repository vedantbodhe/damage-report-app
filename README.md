Report My Damage!

Report My Damage! is a fast, serverless-ready web application that enables users to submit package damage reports via image uploads. Leveraging AWS services (S3, Rekognition, Textract, SES) and OpenAI Vision, it automates damage classification and optional email notifications to package senders. The app features a modern TailwindCSS-powered frontend and is deployed on AWS Elastic Beanstalk with a CI/CD pipeline.

⸻

🚀 Features
	•	Damage Classification: Uses OpenAI Vision (GPT-4 Vision) to classify package damage into categories: scratch, tear, break, dent, or other.
	•	Barcode Processing: (Optional) Scan barcode labels via AWS Rekognition or OpenAI Vision to extract shipment metadata.
	•	OCR Extraction: (Optional) Use AWS Textract to extract text (e.g., email addresses) when notifying senders.
	•	Email Notifications: Send rich HTML email reports with inline images via AWS SES.
	•	Frontend: Responsive, TailwindCSS-based UI with professional branding and user-friendly forms.
	•	Health Checks: Built-in root and /health endpoints for AWS ELB health monitoring.
	•	CI/CD: Integrated GitHub Actions for SAST (CodeQL), secrets scanning (Gitleaks), and automated Elastic Beanstalk deployments.

📦 Tech Stack
	•	Backend: Python 3.11, FastAPI, Uvicorn
	•	Frontend: HTML, TailwindCSS, vanilla JavaScript
	•	AWS Services: S3, Rekognition, Textract, SES, Elastic Beanstalk
	•	AI: OpenAI Vision (gpt-4.1-mini)
	•	CI/CD: GitHub Actions, AWS EB CLI

📥 Prerequisites
	•	AWS Account with IAM user or role having:
	•	S3 full access for the report bucket
	•	Rekognition & Textract permissions
	•	SES send permissions and verified domain/email
	•	Elastic Beanstalk full access
	•	AWS CLI & EB CLI installed and configured
	•	Python 3.10+

🔧 Configuration

Copy .env.example to .env and populate:

# AWS & S3
AWS_REGION=eu-north-1
S3_BUCKET=damage-report-app-fulda

# SES
SES_SOURCE=no-reply@yourdomain.com

# OpenAI
OPENAI_API_KEY=sk-...

Ensure your SES domain/email is verified and DKIM is enabled for deliverability.

🏃 Running Locally
	1.	Clone repository

git clone https://github.com/your-org/damage-report-app.git
cd damage-report-app


	2.	Install dependencies

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


	3.	Run the server

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


	4.	Access
	•	Menu: http://localhost:8000/
	•	Form: http://localhost:8000/form

⚙️ Deployment

Elastic Beanstalk
	1.	Initialize EB

eb init damage-report-app --region eu-north-1 --platform "Python 3.11 running on 64bit Amazon Linux 2023"


	2.	Create environment

eb create damage-env --instance_type t3.micro


	3.	Set environment variables

eb setenv AWS_REGION=eu-north-1 S3_BUCKET=damage-report-app-fulda \
  SES_SOURCE=no-reply@yourdomain.com OPENAI_API_KEY=sk-...


	4.	Deploy updates

git push && eb deploy



Custom Domain & HTTPS
	•	Route 53: Create A/AAAA alias to EB environment.
	•	ACM: Request certificate for reportmydamage.com and www.reportmydamage.com.
	•	Load Balancer: Attach HTTPS listener and select the ACM certificate.

🤖 CI/CD Pipeline
	•	CodeQL for SAST
	•	Gitleaks for secret scanning
	•	Automatic deployments to Elastic Beanstalk on main branch pushes

Configuration file: .github/workflows/ci-cd.yml

🤝 Contributing
	1.	Fork the repo
	2.	Create a feature branch (git checkout -b feat/YourFeature)
	3.	Commit your changes (git commit -m "feat: add ...")
	4.	Push (git push origin feat/YourFeature)
	5.	Open a Pull Request

Please follow our Code of Conduct.

📄 License

This project is licensed under the MIT License. See LICENSE for details.

📫 Contact

– Vedant Bodhe (vedantbodhe99@gmail.com)
– GitHub: @vedantbodhe

⸻

Powered by AWS • FastAPI • OpenAI Vision