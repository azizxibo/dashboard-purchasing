**📊 Purchasing Dashboard – Streamlit Web Application**
📌 Overview

Purchasing Dashboard is a web-based monitoring system developed using Streamlit to support operational purchasing activities.

The application integrates multiple purchasing-related modules into a single analytical interface, enabling structured monitoring, financial visibility, and decision support.

This system transforms spreadsheet-based operational data into an interactive and visual decision-support dashboard.

🚀 Live Application

🔗 Access the Dashboard:
https://dashboard-purchasing-auu9ea7ekaqdaokn3pnqnt.streamlit.app/

**🧩 Core Features**

**💰 1. Petty Cash Monitoring**

- Cashflow tracking (IN / OUT)

- Automatic running balance calculation

- Date filtering and keyword search

- Project / Person in Charge tracking

- PV status indicator (visual highlight)

- KPI summary (Saldo, Total IN, Total OUT, Net)

**🛒 2. Purchase Request Monitoring**

- Project-based filtering

- Search by item or description

- Total estimation calculation

- Distribution visualization per project (interactive pie chart)

- Summary table (Total Estimation & Number of Items)

**📦 3. Cutting Stock Monitoring**

- Safety stock comparison

- Automatic system status:

    - RE-STOCK

    - AMAN

- Priority restock table

- Monitoring dashboard for inventory control

**🔐 4. Protected Entry Mode**

- PIN-based access for internal data entry

- View-only mode for public users

- Structured form for petty cash input

- Designed for future expansion (PR & stock entry)

**📊 Data Architecture**

- Data Source: Google Spreadsheet (Published CSV)

Advantages:

- Real-time operational updates

- No database server required

- Easy maintenance by non-technical users

- Centralized data management

- The application uses:

- Column normalization

- Currency parsing for Indonesian Rupiah format

- Automatic numeric transformation

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

- Support financial monitoring of petty cash

- Enable project-based procurement analysis

- Provide early warning inventory control

- Implement data-driven operational monitoring

- The project demonstrates applied Industrial Engineering concepts in:

- Operational Control

- Inventory Management

- Data Visualization

- Decision Support Systems

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