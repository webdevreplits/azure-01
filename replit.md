# Azure Platform Support WebApp

## Overview

A comprehensive Azure Platform Support web application built with Streamlit that provides a unified portal for operations and platform engineers to manage, monitor, and troubleshoot Azure services. The application features a modern, user-friendly interface with multi-environment support, running seamlessly in Replit, Azure Databricks, and local development environments using the same codebase.

The app includes resource exploration, cost management, incident tracking, performance monitoring, automation tools, and administrative settings. It uses environment auto-detection to dynamically configure database connections, install dependencies, and adapt runtime settings based on the deployment platform.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (October 2025)

### Databricks Deployment Fixes
- **Port Configuration**: Fixed app.yaml to use port 8000 (was 8080) to match Databricks environment expectations
- **Demo User Authentication**: Added automatic demo user creation (demo@azure.com / demo123) when database is available
- **Cost Dashboard Bug**: Fixed NameError in Cost Dashboard by properly initializing Azure client via factory pattern
- **Database Graceful Degradation**: Enhanced pages to handle missing database gracefully, preventing 502 errors
- **Session State Management**: Improved Azure client initialization across pages using session state

### Files Modified
- `app.yaml` - Corrected port from 8080 to 8000 for Databricks
- `core/user_auth.py` - Added ensure_demo_user() method for automatic demo account creation
- `core/login_page.py` - Calls ensure_demo_user() on page load, updated demo credentials hint
- `pages/2_Cost_Dashboard.py` - Fixed Azure client initialization using create_azure_client()
- `pages/3_Incident_Center.py` - Added database availability checks for create/update operations

## System Architecture

### Multi-Environment Detection & Adaptation

**Problem:** Application needs to run across different platforms (Replit, Databricks, local) with platform-specific configurations.

**Solution:** Environment detection system (`env_utils.py`) that identifies the runtime platform by checking environment variables (REPL_ID for Replit, DATABRICKS_RUNTIME_VERSION for Databricks). The system then dynamically configures database connections, package installation, and runtime settings.

**Pros:** Single codebase works everywhere, automatic configuration, reduced maintenance overhead.
**Cons:** Requires careful environment variable management, platform-specific quirks need handling.

### Database Abstraction Layer

**Problem:** Need to support different database systems (PostgreSQL in Replit, Databricks SQL, SQLite fallback) with consistent API.

**Solution:** DatabaseManager class provides unified interface with automatic fallback mechanism. Attempts PostgreSQL connection first (for Replit/Azure), falls back to SQLite if unavailable. Includes schema creation, CRUD operations, and query execution abstracted from underlying DB type.

**Pros:** Database-agnostic application code, automatic failover, easy migration between environments.
**Cons:** Feature parity across different DB systems can be challenging.

### Mock vs Real Azure Client Factory

**Problem:** Development and testing requires Azure data without actual Azure credentials or costs.

**Solution:** Factory pattern (`azure_client_factory.py`) creates either mock or real Azure SDK client based on configuration. Mock client generates realistic sample data for all Azure services. Real client uses Azure SDK for production deployment.

**Pros:** Development without Azure costs, consistent API, easy switching between mock and production.
**Cons:** Mock data may not reflect all real-world edge cases.

### Authentication & Role-Based Access Control

**Problem:** Multi-user access requires authentication and permission management.

**Solution:** UserAuth system with password hashing (PBKDF2), role-based permissions (Admin, Engineer, Viewer), and session management through Streamlit. Roles define permission sets (read, write, delete, admin).

**Pros:** Security through hashing, flexible permissions, simple role hierarchy.
**Cons:** Basic implementation may need enhancement for enterprise use.

### Modular Page Architecture

**Problem:** Complex application with multiple features needs organized structure.

**Solution:** Streamlit multi-page app architecture with dedicated page files (Resource Explorer, Cost Dashboard, Incident Center, Performance Monitor, Tools, Admin Settings). Core utilities in separate module for reusability.

**Pros:** Clear separation of concerns, easy feature addition, independent page development.
**Cons:** Shared state management requires careful coordination via session_state.

### Dynamic Dependency Installation

**Problem:** Different environments have different package availability and installation methods.

**Solution:** DependencyInstaller class checks for missing packages and installs them using environment-appropriate methods (pip for most, dbutils for Databricks). Tracks installed packages to avoid redundant installations.

**Pros:** Automatic setup, environment-aware installation, reduced manual configuration.
**Cons:** Installation failures can be environment-specific and hard to debug.

### Export & Reporting System

**Problem:** Users need to export dashboards and reports in multiple formats.

**Solution:** ExportUtils class provides PDF (using ReportLab) and Excel (using openpyxl) export with formatting. Supports multi-sheet Excel exports and styled PDF reports with tables and charts.

**Pros:** Multiple export formats, professional styling, programmatic generation.
**Cons:** PDF generation complexity, large file sizes for extensive data.

## External Dependencies

### Azure SDK Integration
- **azure-identity**: DefaultAzureCredential for authentication with fallback to ClientSecretCredential and ManagedIdentityCredential
- **azure-mgmt-resource**: Resource Management for subscriptions, resource groups, and resource operations
- **azure-mgmt-costmanagement**: Cost Management API for billing and usage data
- **azure-monitor-query**: MetricsQueryClient and LogsQueryClient for performance metrics and logs
- Optional integration with real Azure services when credentials configured

### Database Systems
- **PostgreSQL**: Primary database for Replit environment via psycopg2, includes RealDictCursor for dictionary results
- **SQLite**: Fallback database for local/offline development
- **Databricks SQL**: Support planned for Databricks SQL Warehouse integration
- Database migration utilities for moving data between environments

### UI & Visualization
- **Streamlit**: Core web framework with multi-page support, session state management, forms and widgets
- **Plotly**: Interactive charts (plotly.express and plotly.graph_objects) for metrics visualization
- **Pandas**: Data manipulation and DataFrame operations throughout the application
- **NumPy**: Numerical operations for mock data generation and calculations

### Export & Reporting
- **ReportLab**: PDF generation with tables, charts, and formatting (SimpleDocTemplate, Table, Paragraph)
- **openpyxl**: Excel file creation with multi-sheet support and cell styling (Font, PatternFill, Alignment, Border)
- Support for exporting dashboards, incident reports, and cost analysis

### Configuration & Environment
- **python-dotenv**: Environment variable loading from .env files
- **PyYAML**: YAML configuration file parsing for config.yaml
- **hashlib & secrets**: Password hashing (PBKDF2) and secure token generation for authentication
- **logging**: Structured logging throughout the application

### Development & Utilities
- **json**: Configuration and data serialization
- **datetime**: Timestamp handling and date range calculations
- **typing**: Type hints for better code clarity and IDE support
- Environment variable based configuration with fallback defaults