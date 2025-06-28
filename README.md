# 🛡️ PolicyPal AI Backend

This is the FastAPI backend for **PolicyPal**, an AI-powered insurance assistant that extracts and analyzes policy documents using Google Gemini (Generative AI).

---

## 📦 Features

- ✅ Upload PDF/Image-based insurance documents
- ✅ Extract raw text and key fields (like insurer, duration, premium)
- ✅ Generate smart summaries using Gemini
- ✅ In-memory job tracking with polling
- ✅ Fast and lightweight backend built for hackathons

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/policypal-backend.git
cd policypal-backend
### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # Linux or macOS
venv\Scripts\activate        # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Your Gemini API Key

Create a `.env` file in the root directory and add:

```env
GEMINI_API_KEY=your-gemini-api-key-here
```

Or export the key from your terminal (for development only):

```bash
export GEMINI_API_KEY=your-gemini-api-key-here   # macOS/Linux
set GEMINI_API_KEY=your-gemini-api-key-here      # Windows
```

### ▶️ Run the FastAPI Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Your backend will now be live at:  
👉 http://localhost:8000
