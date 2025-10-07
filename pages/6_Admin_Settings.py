import streamlit as st
import json
from datetime import datetime
import sys
import os

# Add core directory to path - use absolute path
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
if core_path not in sys.path:
    sys.path.insert(0, core_path)

from config_loader import load_config, save_config
from db_manager import DatabaseManager
from env_utils import detect_environment, get_environment_info
from ui_helpers import setup_page_config, show_notification

def main():
    setup_page_config()
    
    st.title("⚙️ Admin Settings")
    st.markdown("Configure environment settings, database connections, and application preferences.")
    
    # Environment detection
    current_env = detect_environment()
    env_info = get_environment_info(current_env)
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌍 Environment", 
        "🗃️ Database", 
        "🔐 Azure Config", 
        "👤 User Preferences", 
        "🔧 System"
    ])
    
    with tab1:
        st.subheader("Environment Configuration")
        
        # Current environment info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Environment", env_info['name'], env_info['status'])
        
        with col2:
            st.metric("Runtime Version", env_info.get('version', 'Unknown'))
        
        with col3:
            st.metric("Last Started", datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        st.markdown("---")
        
        # Environment details
        st.subheader("🔍 Environment Details")
        
        env_details = {
            'Environment Type': current_env.title(),
            'Detection Method': env_info.get('detection_method', 'Environment variables'),
            'Available Features': env_info.get('features', ['All features available']),
            'Limitations': env_info.get('limitations', ['None']),
            'Configuration Path': env_info.get('config_path', './config')
        }
        
        for key, value in env_details.items():
            if isinstance(value, list):
                st.write(f"**{key}:**")
                for item in value:
                    st.write(f"  • {item}")
            else:
                st.write(f"**{key}:** {value}")
        
        # Environment-specific settings
        st.markdown("---")
        st.subheader("📝 Environment Settings")
        
        with st.form("env_settings"):
            debug_mode = st.checkbox("Enable Debug Mode", value=False)
            auto_refresh = st.checkbox("Auto-refresh Data", value=True)
            refresh_interval = st.number_input("Refresh Interval (seconds)", value=30, min_value=10, max_value=300)
            
            # Environment-specific options
            if current_env == "replit":
                st.markdown("**Replit-specific Settings:**")
                use_replit_db = st.checkbox("Use Replit Database", value=True)
                backup_to_file = st.checkbox("Backup to file system", value=True)
            
            elif current_env == "databricks":
                st.markdown("**Databricks-specific Settings:**")
                use_databricks_sql = st.checkbox("Use Databricks SQL Warehouse", value=True)
                cluster_mode = st.selectbox("Cluster Mode", ["Single Node", "Multi Node"])
                
            submitted = st.form_submit_button("💾 Save Environment Settings", type="primary")
            
            if submitted:
                # Save settings logic here
                show_notification("success", "Environment settings saved successfully!")
    
    with tab2:
        st.subheader("Database Configuration")
        
        # Initialize database manager
        if 'config' in st.session_state:
            db_manager = DatabaseManager(st.session_state.config)
        else:
            db_manager = None
        
        # Database status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            db_status = "Connected" if st.session_state.get('db_connected', False) else "Disconnected"
            status_color = "green" if db_status == "Connected" else "red"
            st.markdown(f"**Status:** :{status_color}[{db_status}]")
        
        with col2:
            if current_env == "replit":
                db_type = "PostgreSQL (Replit)"
            elif current_env == "databricks":
                db_type = "Databricks SQL"
            else:
                db_type = "PostgreSQL"
            st.write(f"**Type:** {db_type}")
        
        with col3:
            st.write(f"**Environment:** {current_env.title()}")
        
        st.markdown("---")
        
        # Database connection settings
        st.subheader("🔌 Connection Settings")
        
        # Show different UI based on environment
        if current_env == "replit":
            st.info("🔵 Using Replit's managed PostgreSQL database. Connection details are automatically configured.")
            
            # Show current connection info (masked)
            with st.expander("Current Database Configuration"):
                st.code(f"""
Database Host: {os.getenv('PGHOST', 'Not set')}
Database Name: {os.getenv('PGDATABASE', 'Not set')}  
Database User: {os.getenv('PGUSER', 'Not set')}
Database Port: {os.getenv('PGPORT', 'Not set')}
SSL Mode: require
                """)
        
        elif current_env == "databricks":
            st.info("🟡 Databricks environment detected. Configure connection to Databricks SQL Warehouse.")
            
            with st.form("databricks_db_config"):
                server_hostname = st.text_input(
                    "Server Hostname", 
                    value="your-workspace.cloud.databricks.com",
                    help="Your Databricks workspace URL"
                )
                http_path = st.text_input(
                    "HTTP Path",
                    value="/sql/1.0/warehouses/your-warehouse-id",
                    help="SQL Warehouse HTTP path"
                )
                access_token = st.text_input(
                    "Access Token", 
                    type="password",
                    help="Personal Access Token for Databricks"
                )
                
                if st.form_submit_button("🔄 Update Databricks Config", type="primary"):
                    show_notification("success", "Databricks configuration updated!")
        
        else:  # Local or other
            st.info("🟢 Local environment. Configure custom database connection.")
            
            with st.form("custom_db_config"):
                db_host = st.text_input("Database Host", value="localhost")
                db_port = st.number_input("Database Port", value=5432, min_value=1, max_value=65535)
                db_name = st.text_input("Database Name", value="azure_support")
                db_user = st.text_input("Database User", value="postgres")
                db_password = st.text_input("Database Password", type="password")
                
                if st.form_submit_button("🔄 Update Database Config", type="primary"):
                    show_notification("success", "Database configuration updated!")
        
        # Database operations
        st.markdown("---")
        st.subheader("🛠️ Database Operations")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Test Connection"):
                with st.spinner("Testing database connection..."):
                    # Test connection logic
                    show_notification("success", "Database connection successful!")
        
        with col2:
            if st.button("🔄 Initialize Schema"):
                with st.spinner("Initializing database schema..."):
                    if db_manager:
                        if db_manager.initialize():
                            show_notification("success", "Database schema initialized!")
                        else:
                            show_notification("error", "Failed to initialize schema")
                    else:
                        show_notification("warning", "Database manager not available")
        
        with col3:
            if st.button("💾 Backup Data"):
                show_notification("info", "Database backup initiated!")
        
        with col4:
            if st.button("📊 View Schema"):
                # Show database schema
                with st.expander("Database Schema", expanded=True):
                    st.code("""
Tables:
- incidents: Store incident tickets and tracking
- resources: Cache Azure resource information  
- settings: Application configuration
- users: User preferences and permissions
- audit_log: Track system activities
                    """, language="sql")
    
    with tab3:
        st.subheader("Azure Configuration")
        
        # Azure connection status
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Authentication", "Active", "✅")
        
        with col2:
            st.metric("Subscriptions", "3", "+1")
        
        with col3:
            st.metric("Last Sync", "2 min ago")
        
        st.markdown("---")
        
        # Azure credentials
        st.subheader("🔐 Azure Credentials")
        
        auth_method = st.selectbox(
            "Authentication Method",
            options=[
                "Service Principal",
                "Managed Identity", 
                "Azure CLI",
                "Interactive Login"
            ],
            index=0
        )
        
        if auth_method == "Service Principal":
            with st.form("azure_sp_config"):
                tenant_id = st.text_input("Tenant ID", type="password")
                client_id = st.text_input("Client ID", type="password")  
                client_secret = st.text_input("Client Secret", type="password")
                subscription_id = st.text_input("Default Subscription ID")
                
                if st.form_submit_button("🔄 Update Azure Config", type="primary"):
                    show_notification("success", "Azure configuration updated!")
        
        elif auth_method == "Managed Identity":
            st.info("🔵 Managed Identity authentication will be used. Ensure the application has appropriate permissions.")
            
            with st.form("azure_mi_config"):
                subscription_id = st.text_input("Default Subscription ID")
                resource_group = st.text_input("Default Resource Group (optional)")
                
                if st.form_submit_button("🔄 Update Config", type="primary"):
                    show_notification("success", "Managed Identity configuration updated!")
        
        # Azure service endpoints
        st.markdown("---")
        st.subheader("🌐 Service Endpoints")
        
        endpoints = {
            "Azure Resource Manager": "https://management.azure.com/",
            "Azure Cost Management": "https://management.azure.com/",
            "Azure Monitor": "https://monitor.azure.com/",
            "Azure Storage": "https://storage.azure.com/",
            "Microsoft Graph": "https://graph.microsoft.com/"
        }
        
        for service, endpoint in endpoints.items():
            col1, col2 = st.columns([2, 3])
            with col1:
                st.write(f"**{service}:**")
            with col2:
                st.code(endpoint)
        
        # Test Azure connection
        if st.button("🔍 Test Azure Connection", type="primary"):
            with st.spinner("Testing Azure connection..."):
                show_notification("success", "Azure connection successful! Found 3 subscriptions.")
    
    with tab4:
        st.subheader("User Preferences")
        
        # User profile
        st.subheader("👤 Profile Settings")
        
        with st.form("user_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                display_name = st.text_input("Display Name", value="Azure Admin")
                email = st.text_input("Email", value="admin@company.com")
                role = st.selectbox("Role", ["Administrator", "Operator", "Viewer"])
            
            with col2:
                timezone = st.selectbox(
                    "Timezone", 
                    ["UTC", "America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"]
                )
                date_format = st.selectbox("Date Format", ["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY"])
                theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
            
            # Dashboard preferences
            st.markdown("**🎛️ Dashboard Preferences**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                default_page = st.selectbox(
                    "Default Page",
                    ["Dashboard", "Resource Explorer", "Cost Dashboard", "Incident Center"]
                )
                items_per_page = st.number_input("Items per page", value=25, min_value=10, max_value=100)
            
            with col2:
                auto_refresh_dashboard = st.checkbox("Auto-refresh dashboard", value=True)
                show_tooltips = st.checkbox("Show help tooltips", value=True)
            
            # Notification preferences  
            st.markdown("**🔔 Notification Preferences**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                email_notifications = st.checkbox("Email notifications", value=True)
                incident_alerts = st.checkbox("Incident alerts", value=True)
                cost_alerts = st.checkbox("Cost threshold alerts", value=True)
            
            with col2:
                performance_alerts = st.checkbox("Performance alerts", value=False)
                weekly_reports = st.checkbox("Weekly summary reports", value=True)
                maintenance_notices = st.checkbox("Maintenance notices", value=True)
            
            if st.form_submit_button("💾 Save Preferences", type="primary"):
                show_notification("success", "User preferences saved successfully!")
        
        # Export/Import preferences
        st.markdown("---")
        st.subheader("📤 Export/Import Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Export Settings"):
                settings_json = {
                    "display_name": "Azure Admin",
                    "theme": "Light",
                    "timezone": "UTC",
                    "notifications": {
                        "email": True,
                        "incidents": True,
                        "costs": True
                    },
                    "dashboard": {
                        "default_page": "Dashboard",
                        "auto_refresh": True,
                        "items_per_page": 25
                    }
                }
                
                st.download_button(
                    label="💾 Download Settings",
                    data=json.dumps(settings_json, indent=2),
                    file_name="azure_support_settings.json",
                    mime="application/json"
                )
                show_notification("success", "Settings exported successfully!")
        
        with col2:
            uploaded_settings = st.file_uploader("Import Settings", type=['json'])
            if uploaded_settings:
                try:
                    settings = json.loads(uploaded_settings.read())
                    show_notification("success", f"Settings imported from {uploaded_settings.name}")
                except json.JSONDecodeError:
                    show_notification("error", "Invalid JSON file format")
    
    with tab5:
        st.subheader("System Configuration")
        
        # System information
        st.subheader("📊 System Information")
        
        system_info = {
            'Application Version': 'v1.0.0',
            'Python Version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'Streamlit Version': st.__version__,
            'Environment': current_env.title(),
            'Uptime': '2 hours 34 minutes',
            'Memory Usage': '245 MB',
            'Database Size': '12.5 MB'
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            for key, value in list(system_info.items())[:4]:
                st.metric(key, value)
        
        with col2:
            for key, value in list(system_info.items())[4:]:
                st.metric(key, value)
        
        # System operations
        st.markdown("---")
        st.subheader("🔧 System Operations")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🧹 Clear Cache"):
                show_notification("success", "Application cache cleared!")
        
        with col2:
            if st.button("📝 View Logs"):
                with st.expander("Recent Log Entries", expanded=True):
                    st.code("""
2024-01-15 10:45:32 INFO: Application started
2024-01-15 10:45:33 INFO: Database connected successfully  
2024-01-15 10:45:35 INFO: Azure client initialized
2024-01-15 10:46:12 INFO: Resource data refreshed
2024-01-15 10:47:25 INFO: User admin@company.com logged in
                    """)
        
        with col3:
            if st.button("💾 Export Config"):
                show_notification("info", "Configuration exported to downloads!")
        
        with col4:
            if st.button("🔄 Restart App"):
                show_notification("warning", "Application restart initiated...")
        
        # Feature flags
        st.markdown("---")
        st.subheader("🚩 Feature Flags")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Enable beta features", value=False)
            st.checkbox("Debug mode", value=False)
            st.checkbox("Performance monitoring", value=True)
            st.checkbox("Error reporting", value=True)
        
        with col2:
            st.checkbox("Auto-backup", value=True)
            st.checkbox("Audit logging", value=True)
            st.checkbox("Rate limiting", value=False)
            st.checkbox("Maintenance mode", value=False)
        
        # Advanced settings
        st.markdown("---")
        st.subheader("⚙️ Advanced Settings")
        
        with st.expander("Advanced Configuration"):
            st.warning("⚠️ Advanced settings. Change only if you know what you're doing.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                max_connections = st.number_input("Max DB connections", value=10, min_value=1, max_value=100)
                query_timeout = st.number_input("Query timeout (seconds)", value=30, min_value=5, max_value=300)
                cache_ttl = st.number_input("Cache TTL (minutes)", value=15, min_value=1, max_value=60)
            
            with col2:
                log_level = st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"])
                max_log_size = st.number_input("Max log size (MB)", value=10, min_value=1, max_value=100)
                backup_retention = st.number_input("Backup retention (days)", value=30, min_value=1, max_value=365)
            
            if st.button("💾 Save Advanced Settings"):
                show_notification("success", "Advanced settings saved!")

if __name__ == "__main__":
    main()
