import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import numpy as np

# Add core directory to path - use absolute path
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
if core_path not in sys.path:
    sys.path.insert(0, core_path)

from azure_client_factory import create_azure_client
from ui_helpers import setup_page_config, show_notification

def main():
    setup_page_config()
    
    st.title("📈 Performance Monitor")
    st.markdown("Monitor Azure services performance metrics and Application Insights data.")
    
    # Initialize Azure client
    azure_client = AzureClient()
    
    # Time range and refresh controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        time_range = st.selectbox(
            "⏱️ Time Range",
            options=["Last Hour", "Last 4 Hours", "Last 24 Hours", "Last 7 Days"],
            index=2
        )
    
    with col2:
        resource_type = st.selectbox(
            "🏭 Resource Type",
            options=["All", "Virtual Machines", "App Services", "SQL Databases", "Storage"],
            index=0
        )
    
    with col3:
        auto_refresh = st.checkbox("🔄 Auto Refresh", value=True)
    
    with col4:
        if st.button("🔄 Refresh Now", type="primary"):
            show_notification("success", "Performance data refreshed!")
            st.rerun()
    
    # Performance overview metrics
    st.markdown("---")
    st.subheader("⚡ Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Average CPU",
            "68.5%",
            delta="5.2%",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Average Memory",
            "72.3%",
            delta="-2.1%",
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "Response Time",
            "245ms",
            delta="15ms",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Error Rate",
            "0.8%",
            delta="-0.2%",
            delta_color="normal"
        )
    
    # Main performance charts
    st.markdown("---")
    st.subheader("📊 Real-time Metrics")
    
    # Generate sample time series data
    time_points = pd.date_range(
        start=datetime.now() - timedelta(hours=24),
        end=datetime.now(),
        freq='5T'
    )
    
    # CPU Usage data
    cpu_data = np.random.normal(65, 15, len(time_points))
    cpu_data = np.clip(cpu_data, 0, 100)
    
    # Memory Usage data
    memory_data = np.random.normal(70, 12, len(time_points))
    memory_data = np.clip(memory_data, 0, 100)
    
    # Response Time data
    response_time = np.random.normal(250, 50, len(time_points))
    response_time = np.maximum(response_time, 50)
    
    metrics_df = pd.DataFrame({
        'Time': time_points,
        'CPU_Usage': cpu_data,
        'Memory_Usage': memory_data,
        'Response_Time': response_time
    })
    
    # CPU and Memory Usage Chart
    fig_usage = go.Figure()
    
    fig_usage.add_trace(go.Scatter(
        x=metrics_df['Time'],
        y=metrics_df['CPU_Usage'],
        mode='lines',
        name='CPU Usage (%)',
        line=dict(color='#FF6B35', width=2)
    ))
    
    fig_usage.add_trace(go.Scatter(
        x=metrics_df['Time'],
        y=metrics_df['Memory_Usage'],
        mode='lines',
        name='Memory Usage (%)',
        line=dict(color='#0078D4', width=2)
    ))
    
    # Add threshold lines
    fig_usage.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="High Usage Threshold")
    fig_usage.add_hline(y=90, line_dash="dash", line_color="darkred", annotation_text="Critical Threshold")
    
    fig_usage.update_layout(
        title='CPU and Memory Usage Over Time',
        xaxis_title='Time',
        yaxis_title='Usage (%)',
        yaxis=dict(range=[0, 100]),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_usage, use_container_width=True)
    
    # Response Time Chart
    fig_response = px.line(
        metrics_df,
        x='Time',
        y='Response_Time',
        title='Response Time Trends',
        labels={'Response_Time': 'Response Time (ms)'}
    )
    
    fig_response.add_hline(y=500, line_dash="dash", line_color="orange", annotation_text="Warning Threshold")
    fig_response.add_hline(y=1000, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
    
    fig_response.update_layout(height=300)
    st.plotly_chart(fig_response, use_container_width=True)
    
    # Resource-specific metrics
    st.markdown("---")
    st.subheader("🏭 Resource Performance Details")
    
    tabs = st.tabs(["Virtual Machines", "App Services", "SQL Databases", "Storage Accounts"])
    
    with tabs[0]:  # Virtual Machines
        st.markdown("### 💻 Virtual Machine Performance")
        
        # VM performance data
        vm_data = {
            'VM Name': ['vm-prod-web-01', 'vm-prod-web-02', 'vm-prod-app-01', 'vm-dev-test-01', 'vm-staging-01'],
            'CPU %': [72, 65, 88, 45, 52],
            'Memory %': [68, 71, 85, 42, 59],
            'Disk I/O': [1250, 980, 1800, 450, 620],
            'Network In': [125, 98, 180, 45, 62],
            'Network Out': [89, 76, 145, 32, 48],
            'Status': ['Healthy', 'Healthy', 'Warning', 'Healthy', 'Healthy']
        }
        
        df_vms = pd.DataFrame(vm_data)
        
        st.dataframe(
            df_vms,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Status': st.column_config.TextColumn(
                    'Status',
                    help='VM health status'
                )
            }
        )
        
        # VM performance heatmap
        vm_metrics = df_vms[['VM Name', 'CPU %', 'Memory %']].set_index('VM Name')
        
        fig_heatmap = px.imshow(
            vm_metrics.T,
            title='VM Resource Utilization Heatmap',
            color_continuous_scale='RdYlBu_r',
            aspect='auto'
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tabs[1]:  # App Services
        st.markdown("### 🌐 App Service Performance")
        
        # App Service metrics
        app_data = {
            'App Name': ['app-frontend', 'app-api', 'app-admin', 'app-mobile-api'],
            'Requests/min': [1250, 890, 340, 567],
            'Avg Response Time': [185, 245, 312, 198],
            'Error Rate %': [0.5, 1.2, 0.8, 0.3],
            'CPU %': [65, 78, 45, 52],
            'Memory %': [72, 85, 58, 63],
            'Health': ['Healthy', 'Warning', 'Healthy', 'Healthy']
        }
        
        df_apps = pd.DataFrame(app_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Requests per minute chart
            fig_requests = px.bar(
                df_apps,
                x='App Name',
                y='Requests/min',
                title='Requests per Minute by App',
                color='Requests/min',
                color_continuous_scale='Blues'
            )
            fig_requests.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_requests, use_container_width=True)
        
        with col2:
            # Response time vs Error rate
            fig_scatter = px.scatter(
                df_apps,
                x='Avg Response Time',
                y='Error Rate %',
                size='Requests/min',
                color='App Name',
                title='Response Time vs Error Rate',
                hover_data=['CPU %', 'Memory %']
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.dataframe(df_apps, use_container_width=True, hide_index=True)
    
    with tabs[2]:  # SQL Databases
        st.markdown("### 🗄️ SQL Database Performance")
        
        # Database metrics
        db_data = {
            'Database': ['prod-userdb', 'prod-orderdb', 'staging-testdb', 'dev-maindb'],
            'DTU Usage %': [72, 85, 45, 38],
            'Connections': [145, 89, 23, 12],
            'Query Duration': [125, 198, 87, 65],
            'Deadlocks/hr': [2, 5, 0, 1],
            'Log Size MB': [1250, 890, 340, 567],
            'Status': ['Healthy', 'Warning', 'Healthy', 'Healthy']
        }
        
        df_dbs = pd.DataFrame(db_data)
        
        # DTU usage chart
        fig_dtu = px.bar(
            df_dbs,
            x='Database',
            y='DTU Usage %',
            title='Database DTU Usage',
            color='DTU Usage %',
            color_continuous_scale='Reds'
        )
        fig_dtu.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="High Usage")
        st.plotly_chart(fig_dtu, use_container_width=True)
        
        st.dataframe(df_dbs, use_container_width=True, hide_index=True)
    
    with tabs[3]:  # Storage Accounts
        st.markdown("### 💾 Storage Account Performance")
        
        # Storage metrics
        storage_data = {
            'Storage Account': ['prodstore001', 'devstore001', 'backupstore001', 'tempstore001'],
            'Used Space GB': [1250, 450, 3400, 89],
            'Transactions/hr': [45000, 12000, 2500, 8900],
            'Ingress MB/s': [125, 45, 890, 23],
            'Egress MB/s': [89, 32, 567, 18],
            'Availability %': [99.98, 99.95, 99.99, 99.92],
            'Health': ['Healthy', 'Healthy', 'Healthy', 'Warning']
        }
        
        df_storage = pd.DataFrame(storage_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Storage usage
            fig_usage = px.pie(
                df_storage,
                values='Used Space GB',
                names='Storage Account',
                title='Storage Usage Distribution'
            )
            st.plotly_chart(fig_usage, use_container_width=True)
        
        with col2:
            # Transactions
            fig_trans = px.bar(
                df_storage,
                x='Storage Account',
                y='Transactions/hr',
                title='Transactions per Hour',
                color='Transactions/hr',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_trans, use_container_width=True)
        
        st.dataframe(df_storage, use_container_width=True, hide_index=True)
    
    # Alerts and thresholds
    st.markdown("---")
    st.subheader("🚨 Performance Alerts")
    
    alerts = [
        {
            'severity': 'warning',
            'message': 'VM vm-prod-app-01 CPU usage above 85% for 15 minutes',
            'time': '2 minutes ago'
        },
        {
            'severity': 'info',
            'message': 'App Service app-api response time increased by 15%',
            'time': '8 minutes ago'
        },
        {
            'severity': 'error',
            'message': 'SQL Database prod-orderdb DTU usage critical (>90%)',
            'time': '12 minutes ago'
        }
    ]
    
    for alert in alerts:
        if alert['severity'] == 'error':
            st.error(f"🔴 {alert['message']} - {alert['time']}")
        elif alert['severity'] == 'warning':
            st.warning(f"🟡 {alert['message']} - {alert['time']}")
        else:
            st.info(f"🔵 {alert['message']} - {alert['time']}")
    
    # Performance recommendations
    st.markdown("---")
    st.subheader("💡 Performance Recommendations")
    
    recommendations = [
        "Consider scaling up vm-prod-app-01 to handle increased CPU load",
        "Review app-api database queries causing increased response time",
        "Archive old data in prod-orderdb to improve performance",
        "Enable auto-scaling for high-traffic app services"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")

if __name__ == "__main__":
    main()
