"""
UI helper functions for Streamlit application.
Provides consistent styling, components, and user interface utilities.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
import io

def setup_page_config():
    """Set up Streamlit page configuration with Azure theme."""
    st.set_page_config(
        page_title="Azure Platform Support",
        page_icon="🔷",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://docs.microsoft.com/azure/',
            'Report a bug': 'mailto:support@company.com',
            'About': """
            # Azure Platform Support Center
            
            A comprehensive web application for managing and monitoring Azure resources.
            
            **Features:**
            - Resource Explorer
            - Cost Management
            - Incident Tracking
            - Performance Monitoring
            - Automation Tools
            - Admin Settings
            
            Version 1.0.0
            """
        }
    )

def display_environment_indicator(environment: str):
    """
    Display environment indicator in the sidebar.
    
    Args:
        environment: Environment type (replit, databricks, local)
    """
    env_colors = {
        'replit': '🟢',
        'databricks': '🔵', 
        'local': '🟡',
        'codespace': '🟢',
        'gitpod': '🟢'
    }
    
    env_names = {
        'replit': 'Replit',
        'databricks': 'Databricks',
        'local': 'Local Dev',
        'codespace': 'Codespace',
        'gitpod': 'Gitpod'
    }
    
    color = env_colors.get(environment, '⚪')
    name = env_names.get(environment, environment.title())
    
    st.sidebar.markdown(
        f"""
        <div style='text-align: center; padding: 10px; margin-bottom: 20px; 
                    background-color: #f0f2f6; border-radius: 10px;'>
            <h3 style='margin: 0; color: #0078D4;'>{color} {name}</h3>
            <p style='margin: 5px 0 0 0; font-size: 0.8em; color: #666;'>
                Environment Active
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_notification(type: str, message: str, duration: int = 3):
    """
    Show notification message to user.
    
    Args:
        type: Notification type ('success', 'error', 'warning', 'info')
        message: Message to display
        duration: Duration to show message (not implemented in Streamlit)
    """
    if type == 'success':
        st.success(f"✅ {message}")
    elif type == 'error':
        st.error(f"❌ {message}")
    elif type == 'warning':
        st.warning(f"⚠️ {message}")
    elif type == 'info':
        st.info(f"ℹ️ {message}")
    else:
        st.write(f"📝 {message}")

def create_metric_card(title: str, value: str, delta: Optional[str] = None, 
                      delta_color: str = "normal") -> None:
    """
    Create a metric card with Azure styling.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Change indicator
        delta_color: Color for delta ('normal', 'inverse', 'off')
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def create_status_badge(status: str) -> str:
    """
    Create a colored status badge.
    
    Args:
        status: Status text
        
    Returns:
        HTML string for status badge
    """
    status_colors = {
        'running': '#28a745',
        'stopped': '#dc3545',
        'starting': '#ffc107',
        'healthy': '#28a745',
        'warning': '#fd7e14',
        'critical': '#dc3545',
        'open': '#007bff',
        'in progress': '#ffc107',
        'resolved': '#28a745',
        'closed': '#6c757d'
    }
    
    color = status_colors.get(status.lower(), '#6c757d')
    
    return f"""
        <span style='
            background-color: {color};
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        '>
            {status}
        </span>
    """

def create_progress_bar(value: float, max_value: float = 100, 
                       color: str = "#0078D4", height: int = 20) -> str:
    """
    Create a custom progress bar.
    
    Args:
        value: Current value
        max_value: Maximum value
        color: Progress bar color
        height: Height in pixels
        
    Returns:
        HTML string for progress bar
    """
    percentage = min((value / max_value) * 100, 100)
    
    return f"""
        <div style='
            width: 100%;
            background-color: #e9ecef;
            border-radius: {height//2}px;
            overflow: hidden;
            height: {height}px;
        '>
            <div style='
                width: {percentage}%;
                background-color: {color};
                height: 100%;
                border-radius: {height//2}px;
                transition: width 0.3s ease;
            '></div>
        </div>
        <div style='text-align: center; font-size: 0.9em; margin-top: 5px;'>
            {value:.1f} / {max_value} ({percentage:.1f}%)
        </div>
    """

def create_info_box(title: str, content: str, icon: str = "ℹ️", 
                   color: str = "#e3f2fd") -> None:
    """
    Create an information box.
    
    Args:
        title: Box title
        content: Box content
        icon: Icon to display
        color: Background color
    """
    st.markdown(
        f"""
        <div style='
            background-color: {color};
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
            border-left: 4px solid #0078D4;
        '>
            <h4 style='margin: 0 0 10px 0; color: #0078D4;'>
                {icon} {title}
            </h4>
            <p style='margin: 0; color: #333;'>
                {content}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def create_collapsible_section(title: str, content: str, expanded: bool = False) -> None:
    """
    Create a collapsible content section.
    
    Args:
        title: Section title
        content: Section content
        expanded: Whether section starts expanded
    """
    with st.expander(title, expanded=expanded):
        st.markdown(content)

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format percentage value.
    
    Args:
        value: Percentage value
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimals}f}%"

def format_timestamp(timestamp: datetime, format_type: str = "datetime") -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp: Datetime object
        format_type: Format type ('datetime', 'date', 'time', 'relative')
        
    Returns:
        Formatted timestamp string
    """
    if format_type == "datetime":
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "date":
        return timestamp.strftime("%Y-%m-%d")
    elif format_type == "time":
        return timestamp.strftime("%H:%M:%S")
    elif format_type == "relative":
        # Simple relative time formatting
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    else:
        return str(timestamp)

def create_data_table(data: List[Dict[str, Any]], 
                     selectable: bool = False,
                     height: Optional[int] = None) -> Any:
    """
    Create an interactive data table.
    
    Args:
        data: List of dictionaries representing table rows
        selectable: Whether rows are selectable
        height: Table height in pixels
        
    Returns:
        Streamlit dataframe component
    """
    if not data:
        st.info("No data available")
        return None
    
    import pandas as pd
    df = pd.DataFrame(data)
    
    # Display the dataframe
    return st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=height
    )

def create_chart_container():
    """Create a container optimized for charts."""
    return st.container()

def add_custom_css():
    """Add custom CSS for Azure theme."""
    st.markdown(
        """
        <style>
        /* Azure theme colors */
        :root {
            --azure-blue: #0078D4;
            --azure-dark-blue: #005A9E;
            --azure-light-gray: #F3F2F1;
            --azure-text: #323130;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: var(--azure-light-gray);
        }
        
        /* Metric styling */
        [data-testid="metric-container"] {
            background-color: white;
            border: 1px solid #e1e5e9;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        
        /* Button styling */
        .stButton > button {
            background-color: var(--azure-blue);
            color: white;
            border-radius: 4px;
            border: none;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            background-color: var(--azure-dark-blue);
        }
        
        /* Header styling */
        .main-header {
            color: var(--azure-blue);
            border-bottom: 2px solid var(--azure-blue);
            padding-bottom: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def export_data_as_csv(data: List[Dict[str, Any]], filename: str) -> str:
    """
    Export data as CSV for download.
    
    Args:
        data: Data to export
        filename: Filename for download
        
    Returns:
        Base64 encoded CSV data
    """
    import pandas as pd
    
    if not data:
        return ""
    
    df = pd.DataFrame(data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    # Create download link
    csv_data = csv_buffer.getvalue()
    b64 = base64.b64encode(csv_data.encode()).decode()
    
    return f'data:file/csv;base64,{b64}'

def create_download_button(data: str, filename: str, label: str = "Download") -> None:
    """
    Create a download button for data.
    
    Args:
        data: Data to download (base64 encoded)
        filename: Filename for download
        label: Button label
    """
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime='text/csv'
    )

def display_loading_spinner(text: str = "Loading..."):
    """
    Display a loading spinner with text.
    
    Args:
        text: Loading text to display
    """
    return st.spinner(text)

def create_tabs(tab_names: List[str]) -> List[Any]:
    """
    Create tabs for content organization.
    
    Args:
        tab_names: List of tab names
        
    Returns:
        List of tab objects
    """
    return st.tabs(tab_names)

def create_columns(num_columns: int, widths: Optional[List[float]] = None) -> List[Any]:
    """
    Create columns for layout.
    
    Args:
        num_columns: Number of columns
        widths: Optional list of column widths
        
    Returns:
        List of column objects
    """
    if widths:
        return st.columns(widths)
    else:
        return st.columns(num_columns)

def display_json(data: Dict[str, Any], expanded: bool = False):
    """
    Display JSON data in an expandable format.
    
    Args:
        data: Dictionary to display as JSON
        expanded: Whether to start expanded
    """
    import json
    
    with st.expander("View JSON Data", expanded=expanded):
        st.json(data)

def create_form(form_key: str) -> Any:
    """
    Create a form for user input.
    
    Args:
        form_key: Unique key for the form
        
    Returns:
        Streamlit form object
    """
    return st.form(key=form_key)

def validate_form_input(input_value: str, field_name: str, 
                       required: bool = True) -> tuple[bool, str]:
    """
    Validate form input.
    
    Args:
        input_value: Value to validate
        field_name: Name of the field
        required: Whether field is required
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if required and not input_value.strip():
        return False, f"{field_name} is required"
    
    return True, ""

def show_success_message(message: str):
    """Show success message."""
    st.success(f"✅ {message}")

def show_error_message(message: str):
    """Show error message."""
    st.error(f"❌ {message}")

def show_warning_message(message: str):
    """Show warning message."""
    st.warning(f"⚠️ {message}")

def show_info_message(message: str):
    """Show info message."""
    st.info(f"ℹ️ {message}")
