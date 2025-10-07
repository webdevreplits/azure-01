import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add core directory to path - use absolute path
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
if core_path not in sys.path:
    sys.path.insert(0, core_path)

from db_manager import DatabaseManager
from ui_helpers import setup_page_config, show_notification

def main():
    setup_page_config()
    
    st.title("🚨 Incident & Support Center")
    st.markdown("Log, track, and resolve Azure service incidents with comprehensive ticket management.")
    
    # Initialize database manager
    if 'config' in st.session_state:
        db_manager = DatabaseManager(st.session_state.config)
    else:
        db_manager = None
        st.error("Database configuration not available. Please check admin settings.")
        return
    
    # Incident overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Open Incidents", "3", "-2")
    
    with col2:
        st.metric("In Progress", "5", "+1")
    
    with col3:
        st.metric("Resolved Today", "12", "+4")
    
    with col4:
        st.metric("Avg Resolution", "4.2 hrs", "-1.3 hrs")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Active Incidents", "➕ New Incident", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Active Incidents")
        
        # Filter and search
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox(
                "Status Filter",
                options=["All", "Open", "In Progress", "Resolved", "Closed"],
                index=0
            )
        
        with col2:
            priority_filter = st.selectbox(
                "Priority Filter",
                options=["All", "Critical", "High", "Medium", "Low"],
                index=0
            )
        
        with col3:
            search_term = st.text_input("🔍 Search incidents", placeholder="Search by title or ID...")
        
        # Sample incident data
        incidents = [
            {
                "ID": "INC-2024-001",
                "Title": "VM Performance Degradation in East US",
                "Status": "In Progress",
                "Priority": "High",
                "Assignee": "Sarah Chen",
                "Created": "2024-01-15 09:30",
                "Service": "Virtual Machines",
                "Description": "Multiple VMs showing high CPU usage and slow response times"
            },
            {
                "ID": "INC-2024-002",
                "Title": "Storage Account Access Issues",
                "Status": "Open",
                "Priority": "Critical",
                "Assignee": "Mike Johnson",
                "Created": "2024-01-15 11:45",
                "Service": "Storage",
                "Description": "Users unable to access blob storage containers"
            },
            {
                "ID": "INC-2024-003",
                "Title": "App Service Deployment Failures",
                "Status": "Resolved",
                "Priority": "Medium",
                "Assignee": "Lisa Wang",
                "Created": "2024-01-14 14:20",
                "Service": "App Services",
                "Description": "Deployment pipeline failing for multiple applications"
            },
            {
                "ID": "INC-2024-004",
                "Title": "SQL Database Connection Timeouts",
                "Status": "In Progress",
                "Priority": "High",
                "Assignee": "David Kim",
                "Created": "2024-01-15 08:15",
                "Service": "SQL Database",
                "Description": "Applications experiencing database connection timeouts"
            },
            {
                "ID": "INC-2024-005",
                "Title": "Network Latency Issues",
                "Status": "Open",
                "Priority": "Low",
                "Assignee": "Emma Davis",
                "Created": "2024-01-15 16:00",
                "Service": "Networking",
                "Description": "Increased network latency between regions"
            }
        ]
        
        df_incidents = pd.DataFrame(incidents)
        
        # Apply filters
        if status_filter != "All":
            df_incidents = df_incidents[df_incidents['Status'] == status_filter]
        
        if priority_filter != "All":
            df_incidents = df_incidents[df_incidents['Priority'] == priority_filter]
        
        if search_term:
            df_incidents = df_incidents[
                df_incidents['Title'].str.contains(search_term, case=False) |
                df_incidents['ID'].str.contains(search_term, case=False)
            ]
        
        # Display incidents table
        st.dataframe(
            df_incidents,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Open", "In Progress", "Resolved", "Closed"],
                    required=True
                ),
                "Priority": st.column_config.SelectboxColumn(
                    "Priority",
                    options=["Critical", "High", "Medium", "Low"],
                    required=True
                )
            }
        )
        
        # Incident details expander
        if not df_incidents.empty:
            selected_incident = st.selectbox(
                "Select incident for details:",
                options=df_incidents['ID'].tolist(),
                index=0
            )
            
            if selected_incident:
                incident_details = df_incidents[df_incidents['ID'] == selected_incident].iloc[0]
                
                with st.expander(f"📋 Incident Details - {selected_incident}", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Title:** {incident_details['Title']}")
                        st.write(f"**Status:** {incident_details['Status']}")
                        st.write(f"**Priority:** {incident_details['Priority']}")
                        st.write(f"**Service:** {incident_details['Service']}")
                    
                    with col2:
                        st.write(f"**Assignee:** {incident_details['Assignee']}")
                        st.write(f"**Created:** {incident_details['Created']}")
                        st.write(f"**ID:** {incident_details['ID']}")
                    
                    st.write(f"**Description:** {incident_details['Description']}")
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("✏️ Edit Incident"):
                            show_notification("info", "Edit mode activated")
                    
                    with col2:
                        if st.button("📝 Add Comment"):
                            show_notification("success", "Comment added successfully")
                    
                    with col3:
                        if st.button("🔄 Update Status"):
                            show_notification("success", "Status updated")
                    
                    with col4:
                        if st.button("📧 Notify Team"):
                            show_notification("info", "Team notification sent")
    
    with tab2:
        st.subheader("Create New Incident")
        
        with st.form("new_incident_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                incident_title = st.text_input("Incident Title*", placeholder="Brief description of the issue")
                incident_priority = st.selectbox("Priority*", options=["Critical", "High", "Medium", "Low"], index=2)
                incident_service = st.selectbox(
                    "Affected Service*",
                    options=["Virtual Machines", "Storage", "App Services", "SQL Database", "Networking", "Other"]
                )
            
            with col2:
                incident_assignee = st.selectbox(
                    "Assignee",
                    options=["Auto-assign", "Sarah Chen", "Mike Johnson", "Lisa Wang", "David Kim", "Emma Davis"]
                )
                incident_region = st.selectbox(
                    "Affected Region",
                    options=["All Regions", "East US", "West US 2", "North Europe", "Southeast Asia"]
                )
                incident_category = st.selectbox(
                    "Category",
                    options=["Performance", "Availability", "Security", "Configuration", "Other"]
                )
            
            incident_description = st.text_area(
                "Detailed Description*",
                placeholder="Provide detailed information about the incident, including symptoms, affected resources, and any troubleshooting steps already taken.",
                height=150
            )
            
            incident_impact = st.text_area(
                "Business Impact",
                placeholder="Describe the impact on business operations, affected users, and any workarounds in place.",
                height=100
            )
            
            submitted = st.form_submit_button("🚨 Create Incident", type="primary")
            
            if submitted:
                if incident_title and incident_description:
                    # Generate new incident ID
                    new_id = f"INC-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
                    
                    # Here you would typically save to database
                    show_notification("success", f"Incident {new_id} created successfully!")
                    
                    # Display created incident summary
                    st.success(f"""
                    **Incident Created Successfully**
                    - **ID:** {new_id}
                    - **Title:** {incident_title}
                    - **Priority:** {incident_priority}
                    - **Assignee:** {incident_assignee}
                    - **Status:** Open
                    """)
                else:
                    show_notification("error", "Please fill in all required fields marked with *")
    
    with tab3:
        st.subheader("Incident Analytics")
        
        # Incident trends
        col1, col2 = st.columns(2)
        
        with col1:
            # Incident status distribution
            status_data = {
                'Status': ['Open', 'In Progress', 'Resolved', 'Closed'],
                'Count': [3, 5, 12, 45]
            }
            df_status = pd.DataFrame(status_data)
            
            fig_status = px.pie(
                df_status,
                values='Count',
                names='Status',
                title='Incident Distribution by Status',
                color_discrete_sequence=['#FF6B6B', '#FFD93D', '#6BCF7F', '#4D96FF']
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Priority distribution
            priority_data = {
                'Priority': ['Critical', 'High', 'Medium', 'Low'],
                'Count': [2, 8, 15, 10]
            }
            df_priority = pd.DataFrame(priority_data)
            
            fig_priority = px.bar(
                df_priority,
                x='Priority',
                y='Count',
                title='Incidents by Priority',
                color='Priority',
                color_discrete_map={
                    'Critical': '#FF4757',
                    'High': '#FF6B35',
                    'Medium': '#F7B731',
                    'Low': '#5F27CD'
                }
            )
            st.plotly_chart(fig_priority, use_container_width=True)
        
        # Service breakdown
        service_data = {
            'Service': ['Virtual Machines', 'Storage', 'App Services', 'SQL Database', 'Networking'],
            'Incidents': [12, 8, 6, 5, 4],
            'Avg Resolution Time': [3.2, 2.1, 4.5, 6.2, 2.8]
        }
        df_services = pd.DataFrame(service_data)
        
        st.subheader("📊 Incidents by Service")
        st.dataframe(
            df_services,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Avg Resolution Time': st.column_config.NumberColumn(
                    'Avg Resolution Time (hours)',
                    format="%.1f"
                )
            }
        )
        
        # Resolution time trends
        st.subheader("⏱️ Resolution Time Trends")
        
        # Generate sample resolution time data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        resolution_times = pd.np.random.normal(4.2, 1.5, len(dates))
        resolution_times = pd.np.maximum(resolution_times, 0.5)  # Ensure positive times
        
        resolution_data = pd.DataFrame({
            'Date': dates,
            'Avg Resolution Time': resolution_times
        })
        
        fig_resolution = px.line(
            resolution_data,
            x='Date',
            y='Avg Resolution Time',
            title='Average Resolution Time Trend (Hours)',
            markers=True
        )
        fig_resolution.add_hline(y=4.2, line_dash="dash", line_color="red", annotation_text="Target: 4.2 hours")
        
        st.plotly_chart(fig_resolution, use_container_width=True)
    
    with tab4:
        st.subheader("Incident Management Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📧 Notification Settings**")
            
            st.checkbox("Email notifications for new incidents", value=True)
            st.checkbox("SMS alerts for critical incidents", value=True)
            st.checkbox("Slack integration", value=False)
            
            notification_frequency = st.selectbox(
                "Digest frequency",
                options=["Real-time", "Hourly", "Daily", "Weekly"]
            )
            
            st.markdown("**⏰ SLA Settings**")
            
            critical_sla = st.number_input("Critical incident SLA (hours)", value=2, min_value=1, max_value=24)
            high_sla = st.number_input("High priority SLA (hours)", value=8, min_value=2, max_value=48)
            medium_sla = st.number_input("Medium priority SLA (hours)", value=24, min_value=8, max_value=72)
        
        with col2:
            st.markdown("**👥 Assignment Rules**")
            
            st.checkbox("Auto-assign based on service type", value=True)
            st.checkbox("Load balancing for assignments", value=True)
            st.checkbox("Escalate unassigned incidents", value=True)
            
            escalation_time = st.number_input("Escalation time (hours)", value=4, min_value=1, max_value=24)
            
            st.markdown("**🔧 Integration Settings**")
            
            st.text_input("Azure Service Health webhook", placeholder="https://...")
            st.text_input("Monitoring system API endpoint", placeholder="https://...")
            
            if st.button("💾 Save Settings", type="primary"):
                show_notification("success", "Settings saved successfully!")

if __name__ == "__main__":
    main()
