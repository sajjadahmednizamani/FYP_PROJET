# 🌍 GoGlobal AI - Smart Immigration & Document Portal

GoGlobal AI is a next-generation, AI-driven immigration assistant designed to simplify the complex process of visa eligibility assessment and document preparation. By leveraging high-performance Large Language Models (LLMs) and real-time data analytics, it empowers students and professionals to seamlessly navigate their global migration journey.

---

## 🚀 Key Features

### 👤 For Users (Applicants)
* **AI Eligibility Engine:** Instant visa success prediction (High / Moderate / Low) based on academic profiles, financial standing, and professional backgrounds.
* **Smart LinkedIn Sync:** Extract professional skills, experience, and key projects directly from a LinkedIn URL or bio using advanced NLP.
* **AI Document Assistant:** Generate highly persuasive, academic-standard Statements of Purpose (SOP) and Cover Letters customized to specific countries in seconds.
* **Professional PDF Export:** Seamlessly download auto-generated documents in a standardized, print-ready PDF format.
* **Real-time Visa News:** Stay up-to-date with a live ticker streaming global immigration policy updates and news.

### 🔐 For Administrators
* **Executive Dashboard:** A secure administrative console featuring real-time interactive charts (Pie & Bar charts) for comprehensive user analytics.
* **Data-Driven Insights:** Monitor global success ratios, application trends, and the most popular target destinations.
* **User Management:** Full CRUD capabilities to manage applicant assessments, track logs, and maintain historical data integrity.

---

## 🧠 AI Architecture & High Availability



---

## 🛠 Tech Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | React.js, Lucide Icons, Recharts (Analytics), jsPDF (Document Generation) |
| **Backend** | FastAPI (Python), Motor (Async MongoDB Driver), Pydantic (Data Validation) |
| **AI Engine** | Google Gemini API (1.5 Flash, 2.0 Flash, 2.5 Flash, Pro) |
| **Database** | MongoDB Atlas (NoSQL cloud database) |

---

## 🏃 Getting Started

### 📋 Prerequisites
Ensure you have the following installed on your system:
* Python 3.9+
* Node.js & npm
* MongoDB Atlas Account
* Google AI (Gemini) API Key

### 🔧 Installation & Setup

#### 1. Clone the Repository
```bash
git clone [https://github.com/sajjadahmednizamani/FYP_PROJET.git](https://github.com/sajjadahmednizamani/FYP_PROJET.git)
cd FYP_PROJET


2. Backend Setup
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
python run.py

3. Frontend Setup
# Open a new terminal window and navigate to frontend directory
cd frontend

# Install npm packages
npm install

# Start the development server
npm start











One of the core technical milestones of this project is its **Model Redundancy & AI Fallback Engine**. To ensure zero downtime and bypass strict API Quota (429 Rate Limit) errors, the backend automatically cycles through multiple Google Gemini models until the request is successfully fulfilled.
