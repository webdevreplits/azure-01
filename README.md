# Azure Platform Support WebApp

A comprehensive, unified Azure Platform Support web application built with Streamlit that runs seamlessly in both Replit and Azure Databricks environments using the same codebase.

![Azure Platform Support](https://img.shields.io/badge/Azure-Platform%20Support-blue?style=for-the-badge&logo=microsoft-azure)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 🎯 Overview

This application provides a modern, user-friendly Azure Platform Support web portal that helps operations and platform engineers easily manage, monitor, and troubleshoot Azure services. The app features automatic environment detection and dynamic configuration for seamless deployment across different platforms.

### ✨ Key Features

- **🔍 Azure Resource Explorer** - Browse and manage Azure resources across subscriptions
- **💰 Cost & Usage Dashboard** - Monitor and analyze Azure spending patterns
- **🚨 Incident & Support Center** - Track and resolve Azure service incidents
- **📈 Performance Monitor** - View Azure Monitor metrics and insights
- **🧰 Tools & Utilities** - Resource management and automation tools
- **⚙️ Admin Settings** - Environment and database configuration management

### 🌍 Multi-Environment Support

- **Replit**: Built-in PostgreSQL, automatic HTTPS, real-time collaboration
- **Azure Databricks**: Databricks SQL Warehouse, Spark integration, MLflow support
- **Local Development**: Custom database setup, full system access

## 🚀 Quick Start

### Option 1: Deploy to Replit

1. **Fork this repository to Replit**
   ```bash
   # The app will automatically detect the Replit environment
   # Database connection is configured automatically
   ```

2. **Configure environment variables** (optional)
   - Copy `.env.example` to `.env`
   - Add your Azure credentials for real Azure data (optional for MVP)

3. **Run the application**
   ```bash
   streamlit run app.py --server.port 5000
   ```

### Option 2: Deploy to Azure Databricks

1. **Clone this repository to your Databricks workspace**
   ```python
   %sh
   git clone https://github.com/your-org/azure-platform-support-app.git
   cd azure-platform-support-app
   ```

2. **Install dependencies** (handled automatically)
   ```python
   %pip install -r requirements.txt
   