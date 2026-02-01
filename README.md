# 🧪 Chemical Equipment Parameter Visualizer

> **Hybrid Web + Desktop Application for Chemical Equipment Analytics**  
> FOSSEE Semester Long Internship 2026 - Screening Task Submission

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.0-61dafb.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Project Overview

A full-stack hybrid application that enables chemical engineers to upload, analyze, and visualize equipment parameter data through both **web browser** and **desktop application** interfaces, powered by a unified Django REST API backend.

### 🎯 Key Features

- ✅ **Dual Frontend**: Web (React.js) + Desktop (PyQt5)
- ✅ **Unified Backend**: Django REST Framework API
- ✅ **Smart Analytics**: Pandas-powered data processing with outlier detection
- ✅ **Visual Insights**: Chart.js (Web) and Matplotlib (Desktop) visualizations
- ✅ **History Management**: Automatic retention of last 5 datasets
- ✅ **PDF Reporting**: Professional equipment analysis reports
- ✅ **Secure Authentication**: JWT-based access control

---

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   React Web     │         │  PyQt5 Desktop  │
│   + Chart.js    │         │  + Matplotlib   │
└────────┬────────┘         └────────┬────────┘
         │                           │
         └───────────┬───────────────┘
                     │ REST API (JWT)
         ┌───────────▼────────────┐
         │   Django + DRF         │
         │   + Pandas Analytics   │
         └───────────┬────────────┘
                     │
         ┌───────────▼────────────┐
         │   SQLite Database      │
         │   (Last 5 Datasets)    │
         └────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Installation

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Web Frontend Setup:**
```bash
cd frontend-web
npm install
npm start
```

**Desktop Frontend Setup:**
```bash
cd frontend-desktop
pip install -r requirements.txt
python main.py
```

---

## 📊 Sample Data Format

The application expects CSV files with the following structure:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A1,Pump,150.5,5.2,85.3
HeatExchanger-B2,Heat Exchanger,200.0,3.8,120.5
Reactor-C3,Reactor,180.2,10.5,250.0
```

---

## 🎥 Demo

[📹 Video Demo (2-3 minutes)](https://youtu.be/your-demo-link)

---

## 🌐 Live Deployment

- **Web App**: https://cepv.raappo.cf
- **API Endpoint**: https://api-cepv.raappo.cf

---

## 👨‍💻 Author

**RAAPPO**  
FOSSEE Internship Candidate 2026  
[GitHub](https://github.com/RAAPPO) | [Portfolio](https://raappo.cf)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Built with ❤️ for FOSSEE IIT Bombay**