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
    
    st.title("💰 Cost & Usage Dashboard")
    st.markdown("Monitor and analyze Azure spending patterns and resource usage costs.")
    
    # Initialize Azure client
    azure_client = AzureClient()
    
    # Time period selector
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        date_range = st.selectbox(
            "📅 Time Period",
            options=["Last 7 days", "Last 30 days", "Last 90 days", "Custom Range"],
            index=1
        )
    
    with col2:
        subscription = st.selectbox(
            "📋 Subscription",
            options=["All Subscriptions", "Production", "Development", "Staging"],
            index=0
        )
    
    with col3:
        if st.button("🔄 Refresh", type="primary"):
            show_notification("success", "Cost data refreshed successfully!")
            st.rerun()
    
    # Cost overview metrics
    st.markdown("---")
    st.subheader("💳 Cost Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Current Month",
            "$15,432.18",
            delta="-$1,234.50 (-7.4%)",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Last Month",
            "$16,666.68",
            delta="$2,100.23 (+14.4%)"
        )
    
    with col3:
        st.metric(
            "Daily Average",
            "$512.74",
            delta="-$41.15 (-7.4%)",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Forecasted",
            "$18,200.00",
            delta="$2,767.82 (+18.0%)"
        )
    
    # Cost trend chart
    st.markdown("---")
    st.subheader("📈 Cost Trends")
    
    # Generate sample cost data
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='D'
    )
    
    daily_costs = np.random.normal(500, 100, len(dates))
    daily_costs = np.maximum(daily_costs, 200)  # Ensure positive costs
    
    cost_data = pd.DataFrame({
        'Date': dates,
        'Cost': daily_costs,
        'Cumulative': np.cumsum(daily_costs)
    })
    
    # Cost trend line chart
    fig_trend = go.Figure()
    
    fig_trend.add_trace(go.Scatter(
        x=cost_data['Date'],
        y=cost_data['Cost'],
        mode='lines+markers',
        name='Daily Cost',
        line=dict(color='#0078D4', width=3),
        marker=dict(size=6)
    ))
    
    fig_trend.add_trace(go.Scatter(
        x=cost_data['Date'],
        y=cost_data['Cost'].rolling(window=7).mean(),
        mode='lines',
        name='7-day Average',
        line=dict(color='#FF6B35', width=2, dash='dash')
    ))
    
    fig_trend.update_layout(
        title='Daily Cost Trends',
        xaxis_title='Date',
        yaxis_title='Cost ($)',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Cost breakdown by service
    st.markdown("---")
    st.subheader("🏭 Cost Breakdown by Service")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Service cost data
        service_costs = {
            'Service': ['Virtual Machines', 'Storage', 'App Services', 'SQL Database', 'Networking', 'Other'],
            'Cost': [6200, 2800, 3400, 1800, 900, 332],
            'Percentage': [40.2, 18.1, 22.0, 11.7, 5.8, 2.2]
        }
        
        df_services = pd.DataFrame(service_costs)
        
        # Pie chart for service costs
        fig_pie = px.pie(
            df_services,
            values='Cost',
            names='Service',
            title='Cost Distribution by Service',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Service cost details table
        st.markdown("**Service Cost Details**")
        st.dataframe(
            df_services.style.format({
                'Cost': '${:,.2f}',
                'Percentage': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Top cost contributors
        st.markdown("**🔝 Top Cost Contributors**")
        for i, row in df_services.head(3).iterrows():
            st.metric(
                f"{row['Service']}",
                f"${row['Cost']:,.2f}",
                f"{row['Percentage']:.1f}%"
            )
    
    # Resource group cost analysis
    st.markdown("---")
    st.subheader("🗂️ Cost by Resource Group")
    
    rg_costs = {
        'Resource Group': ['rg-production', 'rg-development', 'rg-staging', 'rg-shared', 'rg-backup'],
        'Current Month': [8500, 3200, 1800, 1200, 732],
        'Last Month': [9200, 3800, 2100, 1100, 466],
        'Change': [-700, -600, -300, 100, 266]
    }
    
    df_rg = pd.DataFrame(rg_costs)
    df_rg['Change %'] = (df_rg['Change'] / df_rg['Last Month'] * 100).round(1)
    
    # Bar chart for resource group costs
    fig_rg = px.bar(
        df_rg,
        x='Resource Group',
        y='Current Month',
        title='Resource Group Costs - Current Month',
        color='Change %',
        color_continuous_scale='RdYlGn_r',
        text='Current Month'
    )
    
    fig_rg.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig_rg.update_layout(xaxis_tickangle=-45, height=400)
    
    st.plotly_chart(fig_rg, use_container_width=True)
    
    # Cost optimization recommendations
    st.markdown("---")
    st.subheader("💡 Cost Optimization Recommendations")
    
    recommendations = [
        {
            'icon': '🔄',
            'title': 'Right-size Virtual Machines',
            'description': '12 VMs are over-provisioned and can be downsized',
            'potential_saving': '$1,200/month',
            'priority': 'High'
        },
        {
            'icon': '⏰',
            'title': 'Schedule VM Auto-shutdown',
            'description': '8 development VMs running 24/7 unnecessarily',
            'potential_saving': '$800/month',
            'priority': 'Medium'
        },
        {
            'icon': '💾',
            'title': 'Optimize Storage Tiers',
            'description': 'Move infrequently accessed data to cool storage',
            'potential_saving': '$400/month',
            'priority': 'Low'
        },
        {
            'icon': '🗑️',
            'title': 'Remove Unused Resources',
            'description': '5 resources not accessed in 30+ days',
            'potential_saving': '$300/month',
            'priority': 'High'
        }
    ]
    
    for rec in recommendations:
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
            
            with col1:
                st.markdown(f"### {rec['icon']}")
            
            with col2:
                st.markdown(f"**{rec['title']}**")
                st.markdown(f"_{rec['description']}_")
            
            with col3:
                st.metric("Potential Saving", rec['potential_saving'])
            
            with col4:
                priority_color = {
                    'High': 'red',
                    'Medium': 'orange',
                    'Low': 'green'
                }
                st.markdown(f"**Priority:** :{priority_color[rec['priority']]}[{rec['priority']}]")
            
            st.markdown("---")
    
    # Budget and alerts
    st.markdown("---")
    st.subheader("🎯 Budget & Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Budget progress
        budget_amount = 20000
        current_spend = 15432
        budget_progress = (current_spend / budget_amount) * 100
        
        st.metric(
            "Monthly Budget Progress",
            f"${current_spend:,.2f} / ${budget_amount:,.2f}",
            f"{budget_progress:.1f}%"
        )
        
        # Progress bar
        progress_color = 'green' if budget_progress < 75 else 'orange' if budget_progress < 90 else 'red'
        st.progress(budget_progress / 100)
        st.markdown(f":{progress_color}[Budget utilization: {budget_progress:.1f}%]")
    
    with col2:
        st.markdown("**🚨 Active Alerts**")
        alerts = [
            "Budget threshold (75%) exceeded",
            "Daily spend increase detected",
            "Unusual resource usage in rg-production"
        ]
        
        for alert in alerts:
            st.warning(f"⚠️ {alert}")

if __name__ == "__main__":
    main()
