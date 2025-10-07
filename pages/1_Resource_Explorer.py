import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add core directory to path - use absolute path
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
if core_path not in sys.path:
    sys.path.insert(0, core_path)

from azure_client import AzureClient
from ui_helpers import setup_page_config, show_notification

def main():
    setup_page_config()
    
    st.title("🔍 Azure Resource Explorer")
    st.markdown("Browse and manage Azure resources across subscriptions and resource groups.")
    
    # Initialize Azure client
    azure_client = AzureClient()
    
    # Filters section
    with st.expander("🔧 Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_subscription = st.selectbox(
                "Subscription",
                options=["All"] + azure_client.get_subscriptions(),
                index=0
            )
        
        with col2:
            selected_region = st.selectbox(
                "Region",
                options=["All", "East US", "West US 2", "North Europe", "Southeast Asia"],
                index=0
            )
        
        with col3:
            selected_type = st.selectbox(
                "Resource Type",
                options=["All", "Virtual Machines", "Storage Accounts", "App Services", "SQL Databases"],
                index=0
            )
    
    # Resource overview metrics
    st.markdown("---")
    st.subheader("📊 Resource Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Resources", "127", "5 new")
    
    with col2:
        st.metric("Resource Groups", "23", "1 new")
    
    with col3:
        st.metric("Running VMs", "45", "-3")
    
    with col4:
        st.metric("Storage Accounts", "18", "2 new")
    
    # Resource distribution chart
    st.markdown("---")
    st.subheader("📈 Resource Distribution")
    
    # Sample resource data
    resource_data = {
        'Resource Type': ['Virtual Machines', 'Storage Accounts', 'App Services', 'SQL Databases', 'Key Vaults', 'Function Apps'],
        'Count': [45, 18, 23, 12, 8, 15],
        'Status': ['Running', 'Active', 'Running', 'Online', 'Active', 'Running']
    }
    
    df_resources = pd.DataFrame(resource_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart for resource distribution
        fig_pie = px.pie(
            df_resources, 
            values='Count', 
            names='Resource Type',
            title="Resources by Type",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart for resource counts
        fig_bar = px.bar(
            df_resources, 
            x='Resource Type', 
            y='Count',
            title="Resource Counts by Type",
            color='Count',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Resource details table
    st.markdown("---")
    st.subheader("📋 Resource Details")
    
    # Generate sample resource details
    resource_details = []
    for i in range(20):
        resource_details.append({
            'Name': f'resource-{i+1:03d}',
            'Type': pd.np.random.choice(['VM', 'Storage', 'App Service', 'SQL DB']),
            'Resource Group': f'rg-{pd.np.random.choice(["prod", "dev", "staging"])}',
            'Region': pd.np.random.choice(['East US', 'West US 2', 'North Europe']),
            'Status': pd.np.random.choice(['Running', 'Stopped', 'Starting'], p=[0.7, 0.2, 0.1]),
            'Cost/Month': f'${pd.np.random.randint(50, 2000):,}',
            'Tags': f'env:{pd.np.random.choice(["prod", "dev"])}'
        })
    
    df_details = pd.DataFrame(resource_details)
    
    # Search and filter
    search_term = st.text_input("🔍 Search resources", placeholder="Enter resource name or tag...")
    if search_term:
        df_details = df_details[df_details['Name'].str.contains(search_term, case=False)]
    
    # Display the dataframe with styling
    st.dataframe(
        df_details,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Status': st.column_config.SelectboxColumn(
                'Status',
                options=['Running', 'Stopped', 'Starting'],
                required=True
            )
        }
    )
    
    # Action buttons
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refresh Data", type="primary"):
            show_notification("success", "Resource data refreshed successfully!")
            st.rerun()
    
    with col2:
        if st.button("📊 Export Report"):
            show_notification("info", "Resource report exported to downloads!")
    
    with col3:
        if st.button("🏷️ Bulk Tag"):
            show_notification("info", "Bulk tagging interface opened!")
    
    with col4:
        if st.button("🗑️ Cleanup"):
            show_notification("warning", "Resource cleanup wizard started!")
    
    # Resource health status
    st.markdown("---")
    st.subheader("🏥 Resource Health Status")
    
    health_data = {
        'Service': ['Virtual Machines', 'Storage Accounts', 'App Services', 'SQL Databases'],
        'Healthy': [42, 18, 20, 11],
        'Warning': [2, 0, 2, 1],
        'Critical': [1, 0, 1, 0]
    }
    
    df_health = pd.DataFrame(health_data)
    
    # Stacked bar chart for health status
    fig_health = go.Figure()
    
    fig_health.add_trace(go.Bar(
        name='Healthy',
        x=df_health['Service'],
        y=df_health['Healthy'],
        marker_color='#28a745'
    ))
    
    fig_health.add_trace(go.Bar(
        name='Warning',
        x=df_health['Service'],
        y=df_health['Warning'],
        marker_color='#ffc107'
    ))
    
    fig_health.add_trace(go.Bar(
        name='Critical',
        x=df_health['Service'],
        y=df_health['Critical'],
        marker_color='#dc3545'
    ))
    
    fig_health.update_layout(
        title='Resource Health by Service Type',
        xaxis_title='Service Type',
        yaxis_title='Resource Count',
        barmode='stack',
        height=400
    )
    
    st.plotly_chart(fig_health, use_container_width=True)

if __name__ == "__main__":
    main()
