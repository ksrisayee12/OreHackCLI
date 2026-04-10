# 🔐 SecureVisionX

> A full-stack web application for automated vulnerability scanning of source code and web applications, featuring a real-time security dashboard.

![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20React-green)
![Status](https://img.shields.io/badge/status-Active-brightgreen)

---

## 📌 Problem Statement

Intelligent Web Application Vulnerability Detection & Analysis Platform

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🧠 Code Scan | Analyze local codebases using Semgrep to detect security issues with rule-level detail |
| 🌐 External Scan | Perform vulnerability testing on live URLs and web endpoints |
| 📊 Dashboard | Real-time visualization of scan data, severity levels, and risk trends |
| 🧩 History Tracking | Access all past scans with severity breakdowns and timestamps |
| 🧱 Modern UI | Clean, responsive React interface with interactive charts and graphs |
| ⚙️ RESTful API | FastAPI backend with structured endpoints for all scan operations |

---

## 🏗️ Tech Stack

### Frontend
- ⚛️ React.js — Component-based UI
- 🎨 TailwindCSS — Utility-first styling
- 🔗 Axios — API communication
- 📊 Chart.js / Recharts — Data visualization

### Backend
- 🐍 FastAPI (Python) — REST API framework
- 🔍 Semgrep — Static code analysis engine
- 🌐 External vulnerability scanner — URL/endpoint testing
- 💾 JSON-based local storage — Scan history persistence

---

## 📂 Project Structure


```
SecureVisionX/
├── backend/
│   ├── app/
│   │   └── database/
│   │       ├── history_db.py          # Scan history read/write logic
│   │       └── scan_history.json      # Persistent history store
│   ├── scanner/
│   │   ├── code_scanner.py            # Semgrep integration for code scanning
│   │   └── external_scanner.py        # URL-based vulnerability scanning
│   ├── utils/
│   │   └── aggregator.py              # Result aggregation and severity scoring
│   └── main.py                        # FastAPI entry point, all route definitions
│
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   │   └── logo.png
│   │   ├── pages/
│   │   │   ├── Dashboard.js           # Main analytics dashboard
│   │   │   ├── CodeScan.js            # Code scan input and results
│   │   │   ├── ExternalScan.js        # External URL scan interface
│   │   │   ├── History.js             # Past scan history viewer
│   │   │   └── About.js               # Project information page
│   │   ├── App.js                     # Root component and routing
│   │   └── index.css                  # Global styles
│   └── package.json
│
└── README.md
```


---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- Semgrep installed (`pip install semgrep`)

### 1. Clone the Repository

```bash
git clone https://github.com/xxxx/SecureVisionX.git
cd SecureVisionX
````

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://127.0.0.1:8000`
API docs available at `http://127.0.0.1:8000/docs`

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000`

---

## 🧠 How It Works

### Code Scan Flow

1. User provides a local directory path through the UI
2. Backend passes the path to `code_scanner.py` which invokes Semgrep
3. Semgrep runs its rule set against all files in the directory
4. Results (severity, file path, rule ID, description) are returned via API
5. Frontend renders findings with severity color coding
6. Scan result is persisted to `scan_history.json` via `history_db.py`

### External Scan Flow

1. User submits a target URL through the External Scan page
2. `external_scanner.py` runs vulnerability checks against the URL
3. Aggregator combines findings and generates a severity score
4. Results are displayed on-screen and saved to history

### Dashboard Flow

* Dashboard reads aggregated data from scan history
* Charts display total scans, severity distribution, and recent activity
* All data updates in real time as new scans complete

---

## 📈 Scalability

* **Backend** can be containerized with Docker and deployed behind a load balancer to handle concurrent scan requests
* **Scan workers** can be decoupled into background tasks using FastAPI's `BackgroundTasks` or a queue like Celery + Redis, allowing multiple scans to run in parallel
* **History storage** is currently file-based but can be migrated to PostgreSQL or MongoDB with minimal changes to `history_db.py`
* **Frontend** is a static React build that can be served via CDN for global low-latency access

---

## 💡 Feasibility

SecureVisionX is built entirely on production-grade open source tools — FastAPI, React, and Semgrep — that are actively maintained and widely used in industry. The architecture is straightforward (REST API + frontend), deployment requires no specialized infrastructure, and all scanning logic wraps existing tools rather than reinventing them. This makes the project immediately usable in real development workflows with minimal setup.

---

## 🌟 Novelty

Most existing security tools are either CLI-only, require manual configuration per project, or separate code scanning from web scanning into different products. SecureVisionX unifies both workflows — static code analysis and external web scanning — in a single web-based interface with a shared history and dashboard. The combination of Semgrep's rule-based code analysis with an external web scanner in one integrated platform targeted at developers (not just security professionals) is the core novel contribution.

---

## 🔧 Feature Depth

* **Code scanning** supports any language Semgrep supports — Python, JavaScript, Java, Go, Ruby, and more
* **Severity classification** follows industry-standard levels: Critical, High, Medium, Low, Informational
* **History tracking** preserves full scan metadata including timestamps, target, finding count, and severity breakdown
* **Dashboard charts** show trends over time, not just point-in-time snapshots
* **API-first design** means any CI/CD pipeline can call the backend directly without the frontend

---

## ⚠️ Ethical Use & Disclaimer

SecureVisionX is strictly for **educational, research, and authorized security testing only**.

Do **NOT** use this tool to scan or test any system, website, or network without **explicit written permission** from the owner. Unauthorized use may violate cybersecurity laws including the Computer Fraud and Abuse Act (CFAA) and similar legislation in your jurisdiction.

Use responsibly, ethically, and within legal boundaries.

---

## 📜 License

Licensed under the [Apache 2.0 License](LICENSE).

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m "Add feature-name"`
4. Push and open a Pull Request

---

## 🧩 Author

**Sri Sayee K**
📧 [ksrisayee@gmail.com](mailto:ksrisayee@gmail.com)
🔗 [GitHub](https://github.com/xxxx)


---

