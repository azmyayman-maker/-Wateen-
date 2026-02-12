<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/0cd3880b-ab21-4668-92ac-8d891c8a93b7" />


Wateen | وتين

Platform for Home Nursing & Medical Care in Egypt
منصة وتين: الحل الذكي لتنظيم التمريض المنزلي في مصر

<p align="center">
<a href="#about-the-project">About</a> •
<a href="#features">Features</a> •
<a href="#tech-stack">Tech Stack</a> •
<a href="#system-architecture">Architecture</a> •
<a href="#installation-guide">Installation</a> •
<a href="#the-team">The Team</a>
</p>
</div>

📖 About The Project | نبذة عن المشروع

Wateen is a centralized web platform designed to structure and regulate the home nursing market in Egypt. Unlike traditional methods, Wateen acts as a trusted digital link between patients seeking safe care and qualified nurses.

وتين هو مشروع يهدف إلى حل فوضى سوق التمريض المنزلي في مصر. بدلاً من الاعتماد على الوسطاء غير الموثوقين، تقدم منصة "وتين" حلاً مركزياً يربط المرضى بالممريضي المؤهلين بناءً على الموقع الجغرافي، التقييم الذكي، والتحقق من الهوية.

💡 The Problem vs. Solution

The Problem (المشكلة)

The Wateen Solution (الحل)

❌ Lack of Trust: Difficulty verifying nurse credentials. 



 (صعوبة التأكد من هوية ومؤهلات الممرض)

✅ AI Verification: Face recognition & ID matching. 



 (تحقق من الهوية بالذكاء الاصطناعي)

❌ Price Variation: Unregulated pricing per visit. 



 (تفاوت كبير وعشوائي في الأسعار)

✅ Transparent Pricing: Clear hourly/visit rates. 



 (أسعار واضحة ومحددة لكل ممرض)

❌ Random Availability: Hard to find a nurse nearby. 



 (صعوبة العثور على ممرض في نفس المنطقة)

✅ Zone-Based Search: Smart filtering by location. 



 (بحث ذكي بناءً على المنطقة والتخصص)

🚀 Features | المميزات الرئيسية

🏥 For Patients (للمرضى)

Advanced Search: Filter nurses by Zone (e.g., Nasr City, Maadi), Specialty, and Price.

Medical Passport: Create a digital profile with chronic diseases, allergies, and medications.

Smart Booking: Request appointments and track status (Pending -> Accepted -> Completed).

Rating System: Rate nurses after service completion using a 5-star system.

👨‍⚕️ For Nurses (للممرضين)

Professional Profile: Showcase education, experience, and bio in Arabic.

Availability Toggle: Switch status between "Active" and "Busy" with one click.

Request Management: Accept or reject incoming booking requests.

Income Tracking: View completed visits and earnings (simulated dashboard).

🤖 AI & Intelligence (الذكاء الاصطناعي)

Smart Rating Algorithm: Calculates an initial score for new nurses based on Education Level + Years of Experience.

Face Verification: Uses face_recognition & OpenCV to verify the nurse's identity by comparing their uploaded ID with a live selfie.

🛠 Tech Stack | الأدوات والتقنيات

We follow a classic 3-Tier Architecture suitable for educational purposes:

Backend: Python 3 (Flask Framework)

Database: SQLite (wateen.db)

Frontend: HTML5, CSS3 (Custom Design + Flexbox), Vanilla JavaScript (Fetch API)

AI/ML Libraries: face_recognition, opencv-python, scikit-learn

Security: Werkzeug for password hashing, Session-based authentication.

🏗 System Architecture

The connection between the Client (Browser) and the Server (Flask):

sequenceDiagram
    participant User as Browser (JS)
    participant Server as Flask API
    participant DB as SQLite
    
    User->>Server: HTTP Request (JSON)
    Note right of User: e.g., POST /api/login
    Server->>DB: Query Data
    DB-->>Server: Return Result
    Server->>Server: Process Logic / AI
    Server-->>User: JSON Response
    Note right of User: DOM Update (No Reload)


⚡ Installation Guide | دليل التشغيل

To run Wateen locally on your machine, follow these steps:

1. Clone the Repository

git clone [https://github.com/azmyayman-maker/-Wateen-.git](https://github.com/azmyayman-maker/-Wateen-.git)
cd -Wateen-


2. Set Up Virtual Environment (Recommended)

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate


3. Install Dependencies

pip install -r requirements.txt


(Note: If requirements.txt is missing, install: pip install flask face_recognition opencv-python numpy)

4. Initialize Database

# This will create wateen.db and seed it with initial data
python init_db.py


5. Run the Application

python app.py


The application will start at: http://127.0.0.1:5000

📂 Project Structure

Wateen/
├── ai/                     # AI Modules (Face Verify, Smart Rating)
├── database/               # SQL Schema & Database Files
├── static/                 # CSS, JS, Images
├── templates/              # HTML Pages
├── routes/                 # Flask API Routes (Auth, Booking, Profile)
├── app.py                  # Main Application Entry Point
└── README.md               # You are here!


👥 The Team | فريق العمل

Built with Stoics team:

Name

Role

Focus Area

Azmy Ayman

Project Manager

General Management & Integration

(Student Name)

Database Architect

SQL & Schema Design

(Student Name)

API Developer

Flask & Backend Logic

(Student Name)

UI Designer

HTML/CSS & UX

(Student Name)

Frontend Logic

JavaScript & API Integration

(Student Name)

AI Engineer

Computer Vision & Algorithms

(Student Name)

Security & QA

Testing & Validation

📜 License & Disclaimer

This project is an Educational MVP created for university coursework. It is a simulation and not a live medical service.
All medical data used in testing is fictional.

<p align="center">
2024 &copy; Wateen Project. All Rights Reserved.
</p>
