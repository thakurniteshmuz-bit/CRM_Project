# 💼 Enterprise CRM Admin Dashboard

A modern, full-stack Customer Relationship Management (CRM) web application built with **Python**, **Streamlit**, and **MySQL**. This application allows administrators to manage customer profiles, track sales metrics, filter records, and export database reports through a clean, responsive user interface.

---

## ✨ Key Features

- **📊 Interactive Analytics Dashboard**: Real-time overview of total customers, active/inactive status counts, lead tracking, total revenue, and visual product demand charts.
- **➕ Add & Manage Customer Records**: Clean, validated data-entry forms for capturing personal, professional, and purchase details.
- **🔍 Directory Filtering & Search**: Instant keyword search across multiple fields alongside status and product category dropdown filters.
- **📥 CSV Data Export**: One-click export of filtered customer views into downloadable CSV reports.
- **✏️ Full CRUD Operations**: Dedicated workflows to lookup, edit, and safely delete records with confirmation safeguards.
- **⚙️ Automatic Database Setup**: Automatically initializes the required MySQL database and `customers` schema on first launch.

---

## 🛠️ Tech Stack

- **Frontend / UI**: [Streamlit](https://streamlit.io/) + Custom CSS
- **Backend**: Python 3.9+
- **Database**: MySQL (`mysql-connector-python`)
- **Data Processing**: Pandas
- **Security**: `python-dotenv` for environment variable management

---

## 📂 Project Structure

```text
crm-dashboard/
├── app.py               # Main Streamlit application
├── .env                 # Local database credentials (ignored by Git)
├── .env.example         # Template for environment variables
├── .gitignore           # Specifies files excluded from version control
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
