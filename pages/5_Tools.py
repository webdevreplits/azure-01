import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import json

# Add core directory to path - use absolute path
core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'core')
if core_path not in sys.path:
    sys.path.insert(0, core_path)

from azure_client import AzureClient
from ui_helpers import setup_page_config, show_notification

def main():
    setup_page_config()
    
    st.title("🧰 Tools & Utilities")
    st.markdown("Resource management tools, cleanup utilities, and automation helpers for Azure services.")
    
    # Initialize Azure client
    azure_client = AzureClient()
    
    # Tool categories in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗑️ Resource Cleanup", "🤖 Automation", "🔧 Utilities", "📜 Command Console"])
    
    with tab1:
        st.subheader("Resource Cleanup Tools")
        st.markdown("Identify and clean up unused or idle Azure resources to optimize costs.")
        
        # Cleanup options
        cleanup_type = st.selectbox(
            "Cleanup Type",
            options=[
                "Unused Virtual Machines",
                "Orphaned Disks",
                "Empty Resource Groups",
                "Stale Storage Containers",
                "Unused Network Interfaces",
                "Old Snapshots"
            ]
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            age_threshold = st.number_input("Age threshold (days)", value=30, min_value=1, max_value=365)
            include_tags = st.text_input("Include resources with tags", placeholder="env:dev,temp:true")
        
        with col2:
            exclude_tags = st.text_input("Exclude resources with tags", placeholder="critical:true,backup:required")
            dry_run = st.checkbox("Dry run (preview only)", value=True)
        
        if st.button("🔍 Scan for Resources", type="primary"):
            with st.spinner("Scanning for cleanup candidates..."):
                # Simulate resource scanning
                if cleanup_type == "Unused Virtual Machines":
                    cleanup_data = {
                        'Resource Name': ['vm-old-test-01', 'vm-unused-dev-02', 'vm-temp-staging-03'],
                        'Resource Group': ['rg-old-test', 'rg-dev-unused', 'rg-staging-temp'],
                        'Last Activity': ['45 days ago', '67 days ago', '23 days ago'],
                        'Monthly Cost': ['$156', '$234', '$89'],
                        'Size': ['Standard_B2s', 'Standard_D2s_v3', 'Standard_B1s'],
                        'Status': ['Stopped', 'Stopped', 'Running (idle)']
                    }
                elif cleanup_type == "Orphaned Disks":
                    cleanup_data = {
                        'Resource Name': ['disk-orphaned-01', 'disk-unattached-02', 'disk-old-backup-03'],
                        'Resource Group': ['rg-storage', 'rg-compute', 'rg-backup'],
                        'Size (GB)': ['128', '512', '256'],
                        'Monthly Cost': ['$15', '$65', '$32'],
                        'Type': ['Premium SSD', 'Standard SSD', 'Standard HDD'],
                        'Created': ['78 days ago', '45 days ago', '120 days ago']
                    }
                else:
                    cleanup_data = {
                        'Resource Name': ['resource-old-01', 'resource-unused-02'],
                        'Resource Group': ['rg-old', 'rg-unused'],
                        'Type': ['Storage', 'Network'],
                        'Monthly Cost': ['$45', '$23'],
                        'Status': ['Unused', 'Idle'],
                        'Last Used': ['60 days ago', '90 days ago']
                    }
                
                df_cleanup = pd.DataFrame(cleanup_data)
                
                st.success(f"Found {len(df_cleanup)} resources for cleanup")
                
                # Display results
                st.dataframe(df_cleanup, use_container_width=True, hide_index=True)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📊 Generate Report"):
                        show_notification("success", "Cleanup report generated and saved!")
                
                with col2:
                    if st.button("📧 Email Report"):
                        show_notification("info", "Report emailed to administrators!")
                
                with col3:
                    action_text = "Preview Cleanup" if dry_run else "⚠️ Execute Cleanup"
                    if st.button(action_text, type="secondary" if dry_run else "primary"):
                        if dry_run:
                            show_notification("info", f"Dry run completed. {len(df_cleanup)} resources would be cleaned up.")
                        else:
                            show_notification("warning", f"Cleanup initiated for {len(df_cleanup)} resources!")
        
        # Cleanup scheduler
        st.markdown("---")
        st.subheader("📅 Scheduled Cleanup")
        
        with st.expander("Configure Automated Cleanup"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.checkbox("Enable automated cleanup", value=False)
                schedule_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
                notification_email = st.text_input("Notification email", placeholder="admin@company.com")
            
            with col2:
                st.time_input("Run time", value=datetime.now().time())
                max_cost_threshold = st.number_input("Max cost per cleanup ($)", value=1000, min_value=0)
                require_approval = st.checkbox("Require manual approval", value=True)
            
            if st.button("💾 Save Cleanup Schedule"):
                show_notification("success", "Cleanup schedule saved successfully!")
    
    with tab2:
        st.subheader("Automation & Runbooks")
        st.markdown("Trigger automated workflows and manage Azure runbooks.")
        
        # Predefined runbooks
        runbooks = [
            {
                'name': 'VM Auto-Shutdown',
                'description': 'Automatically shut down development VMs outside business hours',
                'status': 'Active',
                'last_run': '2 hours ago',
                'success_rate': '98%'
            },
            {
                'name': 'Storage Tier Optimization',
                'description': 'Move infrequently accessed blobs to cooler storage tiers',
                'status': 'Active',
                'last_run': '1 day ago',
                'success_rate': '95%'
            },
            {
                'name': 'Scale Set Auto-scaling',
                'description': 'Automatically scale VM scale sets based on demand',
                'status': 'Paused',
                'last_run': '3 days ago',
                'success_rate': '92%'
            },
            {
                'name': 'Backup Validation',
                'description': 'Verify backup completion and integrity',
                'status': 'Active',
                'last_run': '6 hours ago',
                'success_rate': '100%'
            }
        ]
        
        # Display runbooks
        for runbook in runbooks:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{runbook['name']}**")
                    st.markdown(f"_{runbook['description']}_")
                
                with col2:
                    status_color = "green" if runbook['status'] == "Active" else "orange"
                    st.markdown(f"Status: :{status_color}[{runbook['status']}]")
                    st.markdown(f"Success: {runbook['success_rate']}")
                
                with col3:
                    st.markdown(f"Last run: {runbook['last_run']}")
                
                with col4:
                    if st.button("▶️", key=f"run_{runbook['name']}", help="Run now"):
                        show_notification("info", f"Triggered runbook: {runbook['name']}")
                
                st.markdown("---")
        
        # Custom automation
        st.subheader("🔧 Custom Automation")
        
        with st.form("custom_automation"):
            automation_name = st.text_input("Automation Name", placeholder="My Custom Script")
            
            col1, col2 = st.columns(2)
            
            with col1:
                trigger_type = st.selectbox("Trigger Type", ["Manual", "Schedule", "Event-based"])
                target_resources = st.multiselect(
                    "Target Resources",
                    options=["All VMs", "Specific Resource Group", "Tagged Resources", "Custom Filter"]
                )
            
            with col2:
                action_type = st.selectbox(
                    "Action Type",
                    ["Start/Stop VMs", "Apply Tags", "Run PowerShell", "Execute ARM Template", "Custom Script"]
                )
                parameters = st.text_area("Parameters (JSON)", placeholder='{"param1": "value1"}')
            
            script_content = st.text_area(
                "Script Content",
                placeholder="# PowerShell or Azure CLI commands\nGet-AzVM | Where-Object {$_.PowerState -eq 'VM running'}",
                height=200
            )
            
            if st.form_submit_button("🚀 Create Automation", type="primary"):
                show_notification("success", f"Automation '{automation_name}' created successfully!")
    
    with tab3:
        st.subheader("Utility Tools")
        st.markdown("Various utilities for Azure resource management and troubleshooting.")
        
        utility_categories = st.selectbox(
            "Select Utility Category",
            options=[
                "Resource Health Check",
                "Cost Calculator",
                "Tag Manager",
                "Backup Validator",
                "Network Diagnostics",
                "Performance Analyzer"
            ]
        )
        
        if utility_categories == "Resource Health Check":
            st.markdown("### 🏥 Resource Health Check")
            
            resource_group = st.selectbox(
                "Select Resource Group",
                options=["All", "rg-production", "rg-development", "rg-staging"]
            )
            
            check_types = st.multiselect(
                "Health Checks to Perform",
                options=[
                    "VM Status Check",
                    "Storage Connectivity",
                    "Network Connectivity",
                    "SSL Certificate Status",
                    "DNS Resolution",
                    "Backup Status"
                ],
                default=["VM Status Check", "Storage Connectivity"]
            )
            
            if st.button("🔍 Run Health Check"):
                with st.spinner("Performing health checks..."):
                    # Simulate health check results
                    health_results = [
                        {"Check": "VM Status Check", "Status": "✅ Passed", "Details": "All 12 VMs are running"},
                        {"Check": "Storage Connectivity", "Status": "✅ Passed", "Details": "All storage accounts accessible"},
                        {"Check": "Network Connectivity", "Status": "⚠️ Warning", "Details": "1 NSG rule may be too permissive"},
                        {"Check": "SSL Certificate Status", "Status": "❌ Failed", "Details": "2 certificates expire in 30 days"}
                    ]
                    
                    df_health = pd.DataFrame(health_results)
                    st.dataframe(df_health, use_container_width=True, hide_index=True)
                    
                    show_notification("info", "Health check completed. Review results above.")
        
        elif utility_categories == "Cost Calculator":
            st.markdown("### 💰 Azure Cost Calculator")
            
            col1, col2 = st.columns(2)
            
            with col1:
                vm_count = st.number_input("Number of VMs", value=1, min_value=0)
                vm_size = st.selectbox("VM Size", ["B1s", "B2s", "D2s_v3", "D4s_v3"])
                storage_gb = st.number_input("Storage (GB)", value=100, min_value=0)
            
            with col2:
                region = st.selectbox("Region", ["East US", "West US 2", "North Europe"])
                hours_per_month = st.slider("Hours per month", 1, 744, 744)
                
                if st.button("💲 Calculate Cost"):
                    # Mock cost calculation
                    vm_cost = vm_count * 50 * (hours_per_month / 744)  # $50 base per month
                    storage_cost = storage_gb * 0.05
                    total_cost = vm_cost + storage_cost
                    
                    st.metric("Estimated Monthly Cost", f"${total_cost:.2f}")
                    st.metric("VM Costs", f"${vm_cost:.2f}")
                    st.metric("Storage Costs", f"${storage_cost:.2f}")
        
        elif utility_categories == "Tag Manager":
            st.markdown("### 🏷️ Resource Tag Manager")
            
            action = st.radio("Action", ["View Tags", "Apply Tags", "Remove Tags"])
            
            if action == "Apply Tags":
                resource_filter = st.text_input("Resource Filter", placeholder="vm-* or resource group name")
                
                col1, col2 = st.columns(2)
                with col1:
                    tag_key = st.text_input("Tag Key", placeholder="Environment")
                with col2:
                    tag_value = st.text_input("Tag Value", placeholder="Production")
                
                if st.button("🏷️ Apply Tags"):
                    show_notification("success", f"Applied tag {tag_key}:{tag_value} to matching resources")
    
    with tab4:
        st.subheader("Command Console")
        st.markdown("Execute Azure CLI commands and PowerShell scripts directly.")
        
        # Command type selector
        command_type = st.selectbox(
            "Command Type",
            options=["Azure CLI", "PowerShell", "REST API"]
        )
        
        # Predefined commands
        st.markdown("**Quick Commands:**")
        
        if command_type == "Azure CLI":
            quick_commands = [
                "az vm list --output table",
                "az group list --output table",
                "az storage account list --output table",
                "az network nsg list --output table",
                "az webapp list --output table"
            ]
        elif command_type == "PowerShell":
            quick_commands = [
                "Get-AzVM | Select-Object Name, ResourceGroupName, PowerState",
                "Get-AzResourceGroup | Select-Object ResourceGroupName, Location",
                "Get-AzStorageAccount | Select-Object StorageAccountName, ResourceGroupName",
                "Get-AzNetworkSecurityGroup | Select-Object Name, ResourceGroupName",
                "Get-AzWebApp | Select-Object Name, ResourceGroup, State"
            ]
        else:  # REST API
            quick_commands = [
                "GET /subscriptions/{subscription-id}/resourceGroups",
                "GET /subscriptions/{subscription-id}/providers/Microsoft.Compute/virtualMachines",
                "GET /subscriptions/{subscription-id}/providers/Microsoft.Storage/storageAccounts",
                "GET /subscriptions/{subscription-id}/providers/Microsoft.Web/sites",
                "GET /subscriptions/{subscription-id}/providers/Microsoft.Network/networkSecurityGroups"
            ]
        
        selected_command = st.selectbox("Select a quick command:", [""] + quick_commands)
        
        # Command input
        command_input = st.text_area(
            f"{command_type} Command:",
            value=selected_command if selected_command else "",
            height=100,
            placeholder=f"Enter your {command_type} command here..."
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("▶️ Execute", type="primary"):
                if command_input.strip():
                    with st.spinner("Executing command..."):
                        # Simulate command execution
                        if "list" in command_input.lower() or "get" in command_input.lower():
                            # Simulate successful list command
                            st.code("""
Command: """ + command_input + """

Result:
Name                    ResourceGroup       Location    Status
----                    -------------       --------    ------
vm-prod-web-01         rg-production       East US     Running
vm-prod-web-02         rg-production       East US     Running  
vm-dev-test-01         rg-development      West US 2   Stopped
vm-staging-app-01      rg-staging          East US     Running

Execution completed successfully.
                            """, language="bash")
                            show_notification("success", "Command executed successfully!")
                        else:
                            st.code(f"""
Command: {command_input}

Result:
Operation completed successfully.
Resources updated: 3
Time taken: 2.4 seconds
                            """, language="bash")
                            show_notification("success", "Command executed successfully!")
                else:
                    show_notification("error", "Please enter a command to execute")
        
        with col2:
            if st.button("📋 Copy"):
                show_notification("info", "Command copied to clipboard!")
        
        with col3:
            if st.button("🗑️ Clear"):
                st.rerun()
        
        # Command history
        st.markdown("---")
        st.subheader("📜 Command History")
        
        # Mock command history
        history = [
            {"Time": "10:45 AM", "Command": "az vm list --output table", "Status": "✅ Success"},
            {"Time": "10:42 AM", "Command": "Get-AzResourceGroup", "Status": "✅ Success"},
            {"Time": "10:38 AM", "Command": "az storage account list", "Status": "⚠️ Warning"},
            {"Time": "10:35 AM", "Command": "Get-AzVM -ResourceGroupName rg-prod", "Status": "✅ Success"},
        ]
        
        df_history = pd.DataFrame(history)
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        
        # Export/Import commands
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Export History"):
                show_notification("success", "Command history exported to file!")
        
        with col2:
            uploaded_file = st.file_uploader("Import Commands", type=['txt', 'ps1', 'sh'])
            if uploaded_file:
                show_notification("info", f"Imported commands from {uploaded_file.name}")

if __name__ == "__main__":
    main()
