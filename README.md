**📊 Purchasing Dashboard – Streamlit Web Application**

**📌 Overview**

Purchasing Dashboard is a web-based operational monitoring system developed using Streamlit to support purchasing, petty cash management, and inventory control activities.

This application transforms spreadsheet-based operational data into an interactive analytical dashboard, enabling:

    - Structured financial monitoring
    - Real-time purchasing visibility
    - Inventory status control
    - Project-based spending analysis
    - Data-driven decision support

The system integrates multiple operational modules into a single interface to improve transparency and efficiency within purchasing activities.

**🚀 Live Application**

🔗 Access the Dashboard:
https://dashboard-purchasing-auu9ea7ekaqdaokn3pnqnt.streamlit.app/

**🧩 Core Features**

**💰 1. Petty Cash Monitoring**

- IN / OUT cashflow tracking

- Automatic running balance calculation

- Date range filtering

- Keyword search (description / project / PIC)

- Project / Person in Charge tracking

- PV (Payment Voucher) status indicator with visual highlighting

- KPI summary:

    - Saldo Akhir

    - Total IN

    - Total OUT

    - Net Cashflow

    - Total Transactions

- Monthly cashflow breakdown:

    - IN

    - OUT

    - NET

- Automatic monthly insight generation

- Top spending project visualization (Horizontal Bar Chart with Top 1 highlight)

**🛒 2. Purchase Request Monitoring**

- Project-based filtering

- Item / description search

- Automatic subtotal parsing (Indonesian Rupiah format)

- Total estimation calculation

- Interactive project distribution visualization (Donut Chart – Plotly)

- Summary table:

    - Total Estimation per Project

    - Number of Items per Project

**📦 3. Cutting Stock Monitoring**

- Quantity vs Safety Stock comparison

- Automatic system status classification:

    - RE-STOCK

    - AMAN

- Priority restock table

- Inventory monitoring dashboard

- Early warning for stock shortage

**🔎 4. Price & Supplier Tracking (Protected Mode)**

- Item-based price search

- Supplier comparison

- Historical price analytics:

    - Lowest price

    - Highest price

    - Average price

- Most frequently used supplier identification

- Restricted access via PIN authentication

**🔐 Access Control System**

- PIN-based authentication system

- Public users → View-only mode

- Staff mode → Internal tracking & analysis access

- Designed for future expansion:

    - Purchase entry form

    - Stock entry

    - Internal operational management

**📊 Data Architecture**

- Data Source: Google Spreadsheet (Published CSV)

Advantages:

- Real-time operational updates

- No database server required

- Easy maintenance by non-technical users

- Centralized data management

- Lightweight deployment architecture

Data Processing Includes:

- Column normalization

- Robust Indonesian Rupiah parsing

- Automatic numeric transformation

- Running balance computation

- Monthly aggregation

- Cached data loading for performance optimization

**🔄 Update Mechanism**

- Data is loaded via @st.cache_data

- Manual refresh button available

- Automatic refresh on reload

- Short delay possible due to caching policy (TTL)

**🛠️ Tech Stack**

- Python 3.10+

- Streamlit

- Pandas

- NumPy

- Plotly

- Google Spreadsheet (CSV endpoint)

- Streamlit Cloud (Deployment)

**🎯 System Objectives**

- This dashboard was developed to:

- Improve transparency in purchasing operations

- Monitor petty cash financial flow

- Analyze procurement spending per project

- Provide inventory early warning control

- Implement structured data-driven operational monitoring

**📘 Applied Industrial Engineering Concepts**

- This project demonstrates practical implementation of:

- Operational Control

- Inventory Management

- Cashflow Monitoring

- Data Visualization

- Decision Support Systems

- Applied Analytics in Operational Environment

📁 Project Structure

    ├── app.py
    ├── requirements.txt
    ├── README.md

👤 Author

**Aziz Ramdhani**

*Industrial Engineering ⚙️ – President University 🎓*

*Purchasing Staff Intern Project 💼🛒📦📊*

**📄 License**

This project is developed for academic and professional portfolio purposes.