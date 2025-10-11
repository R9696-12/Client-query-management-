# 📂 Client Query Management System

This project is a full-stack Python + MySQL web application built with Streamlit, designed to streamline customer support operations. It provides clients with an intuitive interface to submit their queries while enabling support teams to monitor, assign, and resolve issues systematically..

## 🚀 Overview

* 🔐 **Role-based Access**: Clients submit queries, Support Staff resolve them.
* 📝 **Query Submission**: Capture client details like email, mobile, heading & description.
* 📊 **Support Dashboard**: Filter, view, and close queries in real-time.
* 💾 **Persistent Storage**: Queries & users stored in **MySQL**.
* ⚡ **Analytics Ready**: Monitor open vs closed tickets, response times, and trends.

---

## 🛠️ Tech Stack

* **Frontend / UI**: Streamlit
* **Backend / Core**: Python
* **Database**: MySQL
* **Data Handling**: Pandas
* **Security**: hashlib (password hashing)

---

## 🔧 Installation & Setup

### 1️⃣ Database Setup

```sql
CREATE DATABASE query_management_db;
python -m venv venv
# Activate environment
venv\Scripts\activate      # (Windows)

# Install packages
pip install -r requirements.txt
streamlit
pandas
mysql
```

* Update `database.py` with your MySQL credentials:

```python
connection = mysql.connector.connect(
    host='localhost',
    database='query_management_db',
    user='root',
    password='Ravi@123'   # change if necessary
)
```

### 2️⃣ Install Dependencies

```bash
pip install streamlit pandas mysql-connector-python
```

### 3️⃣ Initialize Database

```bash
database.py,query.py,app_run.py - all in one at single_app.py
```

### 4️⃣ Run the App

```bash
streamlit run .vscode\single_app.py
```

---

## ✨ Core Features

✅ **Role-Based Login**: Separate Client & Support interfaces
✅ **Query Submission**: Clients raise tickets with details
✅ **Support Dashboard**: View & filter open/closed queries
✅ **Query Resolution**: Close tickets with auto timestamp
✅ **CSV Import**: Load initial synthetic data

---

## 📸 Screenshots (Optional)

* screenshots of your Client Submission page & Support Dashboard here.*
[screenshots of apprun.pdf](https://github.com/user-attachments/files/22710271/screenshots.of.apprun.pdf)






