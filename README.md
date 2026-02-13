# Future Financial Readiness System

A full-stack Flask web application that evaluates a user’s financial readiness
based on income, expenses, savings behavior, and emergency preparedness.
The system provides personalized insights, behavioral memory, and historical tracking
to help users understand and improve their financial decisions.

---

## 🚀 Key Features

- 🔐 Secure user-based session handling
- 📊 Financial readiness score (0–100)
- 🧠 Behavioral resistance detection
- 🔁 Behavioral memory (learns from past improvements)
- 📈 Dashboard with trend indicators
- 🗂 Monthly readiness history tracking
- 📄 Downloadable PDF history report
- 🧹 One-click history clearing with confirmation
- 📊 Visual charts (savings vs expenses, expense split)
- 🧾 Detailed evaluation report with insights
- 🛡 Data & trust transparency (no ads, no tracking)

---

## 🧠 How the System Works

The system evaluates financial readiness using:
- Income vs expenses ratio
- Fixed vs variable expense balance
- Savings consistency
- Emergency fund availability
- Behavioral resistance patterns

Each assessment generates:
- Readiness score and level
- Personalized action plan
- Behavioral memory insight
- Visual financial analysis
- Historical comparison

---

## 🛠 Tech Stack

### Backend
- Python
- Flask
- SQLite
- Pandas

### Data & Reports
- Matplotlib (charts)
- ReportLab (PDF generation)

### Frontend
- HTML (Jinja2 templates)
- CSS (custom fintech-style UI)

---

## 📂 Project Structure

future-readiness-system/
├── core/ # Financial logic & scoring engine
├── data/ # SQLite database
├── reports/ # Generated reports (optional)
├── web/
│ ├── app.py # Flask application
│ ├── templates/ # HTML templates
│ ├── static/
│ │ ├── style.css
│ │ └── plots/
│ └── plots/ # Generated charts

---

## ⚙️ Installation & Local Setup

1. Clone the repository
2. Navigate to the `web` directory
3. Install dependencies:
pip install flask pandas matplotlib reportlab
4. Run the application:
   python app.py
5. Open in browser:
   http://127.0.0.1:5000

---

## 📄 Reports & History

- Evaluation reports are generated per assessment
- Readiness history is stored securely per user
- History can be downloaded as a **PDF**
- Users can clear history at any time

---

## 🔐 Privacy & Trust

- No advertisements
- No third-party analytics
- No sensitive financial data storage
- Only summary history is saved for user insight
- Designed for educational and personal awareness

---

## ⚠️ Disclaimer

This system is intended for **educational and personal insight purposes only**.
It does not provide professional financial advice.

---

## 👤 Author

**Bavya Sri Sai Thatipudi**  
Built as a full-stack financial analytics project using Python & Flask.
