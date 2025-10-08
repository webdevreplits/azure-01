"""
Login page component for Streamlit app.
"""

import streamlit as st
from typing import Optional, Dict, Any
from user_auth import UserAuth
from db_manager import DatabaseManager

def show_login_page(db_manager: DatabaseManager) -> Optional[Dict[str, Any]]:
    """
    Display login page and handle authentication.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        User dictionary if authenticated, None otherwise
    """
    # Initialize auth
    auth = UserAuth(db_manager)
    auth.ensure_schema()
    auth.ensure_demo_user()  # Create demo user if it doesn't exist
    
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🔷 Azure Platform")
        st.markdown("## Support Center")
        st.markdown("---")
        
        # Check if we should show registration
        show_register = st.session_state.get('show_register', False)
        
        if not show_register:
            # Login form
            st.markdown("### 🔐 Sign In")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                col_login, col_reg = st.columns(2)
                
                with col_login:
                    submit = st.form_submit_button("🔓 Sign In", type="primary", use_container_width=True)
                
                with col_reg:
                    if st.form_submit_button("📝 Register", use_container_width=True):
                        st.session_state.show_register = True
                        st.rerun()
                
                if submit:
                    if username and password:
                        user = auth.authenticate(username, password)
                        if user:
                            st.session_state.user = user
                            st.session_state.authenticated = True
                            st.success(f"Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.warning("Please enter both username and password")
            
            # Demo credentials hint
            st.info("💡 **Demo Credentials**: Username: `demo@azure.com` | Password: `demo123`")
        
        else:
            # Registration form
            st.markdown("### 📝 Create Account")
            
            with st.form("register_form"):
                new_username = st.text_input("Username", placeholder="Choose a username")
                new_email = st.text_input("Email", placeholder="your.email@company.com")
                new_password = st.text_input("Password", type="password", placeholder="Choose a strong password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                
                st.info("📌 New accounts are created with 'Viewer' role. Contact admin to upgrade permissions.")
                
                col_reg, col_back = st.columns(2)
                
                with col_reg:
                    submit_reg = st.form_submit_button("✅ Create Account", type="primary", use_container_width=True)
                
                with col_back:
                    if st.form_submit_button("← Back to Login", use_container_width=True):
                        st.session_state.show_register = False
                        st.rerun()
                
                if submit_reg:
                    if not all([new_username, new_email, new_password, confirm_password]):
                        st.error("Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        try:
                            if auth.create_user(new_username, new_password, new_email, role='Viewer'):
                                st.success("Account created successfully! Please sign in.")
                                st.session_state.show_register = False
                                st.rerun()
                            else:
                                st.error("Failed to create account. Username may already exist.")
                        except Exception as e:
                            st.error(f"Registration failed: {str(e)}")
    
    return None

def show_user_menu():
    """Display user menu in sidebar."""
    if 'user' in st.session_state and st.session_state.get('authenticated'):
        user = st.session_state.user
        
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"### 👤 {user['username']}")
            st.caption(f"Role: {user['role']}")
            st.caption(f"Email: {user.get('email', 'N/A')}")
            
            if st.button("🚪 Sign Out", use_container_width=True):
                # Clear session state
                for key in ['user', 'authenticated', 'azure_client', 'db_manager']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

def require_permission(permission: str) -> bool:
    """
    Check if current user has required permission.
    
    Args:
        permission: Required permission
        
    Returns:
        True if user has permission, False otherwise
    """
    if 'user' not in st.session_state or not st.session_state.get('authenticated'):
        st.error("🔒 Please sign in to access this feature")
        return False
    
    user = st.session_state.user
    if permission not in user.get('permissions', []):
        st.error(f"🔒 Insufficient permissions. Required: {permission}")
        st.info(f"Your role ({user.get('role')}) does not have '{permission}' permission.")
        return False
    
    return True
