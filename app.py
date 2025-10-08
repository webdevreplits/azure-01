import streamlit as st
import os
import sys
from datetime import datetime

# Add core directory to path - use absolute path
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core')
if core_path not in sys.path:
    sys.path.insert(0, core_path)

from env_utils import detect_environment, get_environment_info
from config_loader import load_config
from db_manager import DatabaseManager
from installer import check_and_install_dependencies
from ui_helpers import setup_page_config, display_environment_indicator, show_notification
from login_page import show_login_page, show_user_menu

def main():
    # Set up page configuration
    setup_page_config()
    
    # Initialize session state
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.db_connected = False
        st.session_state.authenticated = False
        st.session_state.environment = detect_environment()
        st.session_state.config = load_config()
    
    # Initialize database first (needed for authentication)
    if not st.session_state.initialized:
        with st.spinner("Initializing Azure Platform Support Center..."):
            try:
                # Check dependencies
                check_and_install_dependencies(st.session_state.environment)
                
                # Initialize database
                db_manager = DatabaseManager(st.session_state.config)
                if db_manager.initialize():
                    st.session_state.db_connected = True
                    st.session_state.db_manager = db_manager
                else:
                    st.session_state.db_connected = False
                
                st.session_state.initialized = True
                
            except Exception as e:
                st.error(f"Initialization failed: {str(e)}")
                return
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        show_login_page(st.session_state.db_manager)
        return
    
    # Display environment indicator and user menu in sidebar
    with st.sidebar:
        display_environment_indicator(st.session_state.environment)
        show_user_menu()
        
        # Navigation
        st.markdown("---")
        st.markdown("### 🧭 Navigation")
        st.markdown("Use the pages in the sidebar to navigate through different sections of the Azure Platform Support app.")
    
    # Main content area
    st.title("🔷 Azure Platform Support Center")
    
    # Environment information
    env_info = get_environment_info(st.session_state.environment)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Environment", env_info['name'], env_info['status'])
    with col2:
        st.metric("Database", "PostgreSQL", "Connected" if st.session_state.db_connected else "Disconnected")
    with col3:
        st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))
    
    
    # Main dashboard content
    st.markdown("---")
    
    # Quick stats dashboard
    st.subheader("📊 Platform Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Active Resources",
            value="127",
            delta="5 this week"
        )
    
    with col2:
        st.metric(
            label="Total Cost (Monthly)",
            value="$15,432",
            delta="-$1,234 from last month"
        )
    
    with col3:
        st.metric(
            label="Active Incidents",
            value="3",
            delta="-2 from yesterday"
        )
    
    with col4:
        st.metric(
            label="Performance Score",
            value="94%",
            delta="2% improvement"
        )
    
    # Feature overview
    st.markdown("---")
    st.subheader("🚀 Available Features")
    
    features = [
        {"icon": "🔍", "title": "Resource Explorer", "desc": "Browse and manage Azure resources across subscriptions"},
        {"icon": "💰", "title": "Cost Dashboard", "desc": "Monitor and analyze Azure spending patterns"},
        {"icon": "🚨", "title": "Incident Center", "desc": "Track and resolve Azure service incidents"},
        {"icon": "📈", "title": "Performance Monitor", "desc": "View Azure Monitor metrics and insights"},
        {"icon": "🧰", "title": "Tools & Utilities", "desc": "Resource management and automation tools"},
        {"icon": "⚙️", "title": "Admin Settings", "desc": "Configure environment and database settings"},
    ]
    
    cols = st.columns(2)
    for i, feature in enumerate(features):
        with cols[i % 2]:
            with st.container():
                st.markdown(f"**{feature['icon']} {feature['title']}**")
                st.markdown(f"_{feature['desc']}_")
                st.markdown("---")
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; padding: 20px;'>
            Azure Platform Support Center v1.0 | Environment: {env_info['name']} | 
            Running on {st.session_state.environment.title()}
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
