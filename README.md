# Report My Damage!

https://www.reportmydamage.com (currently disabled)

Report My Damage! is a fast, serverless-ready web application that enables users to submit package damage reports via image uploads. Leveraging AWS services (S3, Rekognition, Textract, SES) and OpenAI Vision, it automates damage classification and optional email notifications to package senders. The app features a modern TailwindCSS-powered frontend and is deployed on AWS Elastic Beanstalk with a CI/CD pipeline.

⸻

🚀 Features

 - Damage Classification: Uses OpenAI Vision (GPT-4 Vision) to
   classify package damage into categories: scratch, tear, break, dent,
   or other. 
   
 - Barcode Processing: (Optional) Scan barcode labels via
   AWS Rekognition or OpenAI Vision to extract shipment metadata. 	
 - Email Notifications: Send rich
   HTML email reports with inline images via AWS SES. 	
 - Frontend: Responsive, TailwindCSS-based UI with professional branding and
   user-friendly forms. 	
 - Health Checks: Built-in root and /health
   endpoints for AWS ELB health monitoring. 	
   
 - CI/CD: Integrated GitHub Actions for SAST (CodeQL) and secrets scanning (Gitleaks).

   
 - OCR Extraction: (Work in Progress) Use AWS Textract to extract text (e.g., email
   addresses) when notifying senders. 	

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

## AWS & S3
AWS_REGION=eu-north-1
S3_BUCKET=damage-report-app-fulda

## SES
SES_SOURCE=no-reply@yourdomain.com

## OpenAI
OPENAI_API_KEY=sk-...

Ensure your SES domain/email is verified and DKIM is enabled for deliverability.

🏃 Running Locally

1.	Clone repository

```sh
git clone https://github.com/your-org/damage-report-app.git
cd damage-report-app
```

2.	Install dependencies

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3.	Run the server

```sh
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

 4. Access
	
 - Menu: http://localhost:8000/
 - Form: http://localhost:8000/form

⚙️ Deployment

Elastic Beanstalk
1.	Initialize EB

```sh
eb init damage-report-app --region eu-north-1 --platform "Python 3.11 running on 64bit Amazon Linux 2023"
```

2.	Create environment
```sh
eb create damage-env --instance_type t3.micro
```

3.	Set environment variables
```sh
eb setenv AWS_REGION=eu-north-1 S3_BUCKET=damage-report-app-fulda \
  SES_SOURCE=no-reply@yourdomain.com OPENAI_API_KEY=sk-...
```

4.	Deploy updates
```sh
git push && eb deploy
```

🤖 CI/CD Pipeline
	•	CodeQL for SAST
	•	Gitleaks for secret scanning
	•	Automatic deployments to Elastic Beanstalk on main branch pushes

Configuration file: .github/workflows/ci-cd.yml

🤝 Contribution only per official contact: vedantbodhe@gmail.com

Please follow our Code of Conduct.

📄 License

### I would love to collaborate on this project!
### Please feel free to contact in this case.
### Copyright laws apply.

Copyright (c) 2025 Vedant Vinayak Bodhe. All rights reserved.

This software and its associated files are the exclusive property of Vedant Vinayak Bodhe.

You are not permitted to copy, modify, merge, publish, distribute, sublicense, and/or sell copies of this software, in whole or in part, without the express prior written permission or credit of the copyright holder. 

Any unauthorized sale of this software is strictly prohibited and may result in legal action.

Contact: vedantbodhe@gmail.com for licensing and work inquiries.

📫 Contact

– Vedant Bodhe (vedantbodhe@gmail.com)
– GitHub: @vedantbodhe

⸻

Powered by AWS • FastAPI • OpenAI Vision
