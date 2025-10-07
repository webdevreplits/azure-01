"""
Mock Azure Client for MVP implementation.
This simulates Azure SDK functionality for development and testing.
Replace with real Azure SDK calls in production.
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

class AzureClient:
    """
    Mock Azure client that simulates Azure SDK functionality.
    Provides realistic sample data for development and testing.
    """
    
    def __init__(self):
        self.subscriptions = [
            "Production Subscription",
            "Development Subscription", 
            "Staging Subscription"
        ]
        
        self.resource_groups = [
            "rg-production",
            "rg-development", 
            "rg-staging",
            "rg-shared",
            "rg-backup"
        ]
        
        self.regions = [
            "East US",
            "West US 2", 
            "North Europe",
            "Southeast Asia",
            "UK South"
        ]
        
        self.resource_types = [
            "Virtual Machines",
            "Storage Accounts",
            "App Services", 
            "SQL Databases",
            "Key Vaults",
            "Function Apps",
            "Container Instances",
            "Kubernetes Services"
        ]
    
    def get_subscriptions(self) -> List[str]:
        """Get list of available Azure subscriptions."""
        return self.subscriptions
    
    def get_resource_groups(self, subscription_id: Optional[str] = None) -> List[str]:
        """Get list of resource groups for a subscription."""
        return self.resource_groups
    
    def get_resources(self, resource_group: Optional[str] = None, 
                     resource_type: Optional[str] = None,
                     region: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of Azure resources with optional filtering.
        
        Args:
            resource_group: Filter by resource group
            resource_type: Filter by resource type
            region: Filter by region
            
        Returns:
            List of resource dictionaries
        """
        resources = []
        
        # Generate sample resources
        for i in range(50):
            resource = {
                'id': f'/subscriptions/sub-{i:03d}/resourceGroups/{random.choice(self.resource_groups)}/providers/Microsoft.Compute/resource-{i:03d}',
                'name': f'resource-{i:03d}',
                'type': random.choice(self.resource_types),
                'resource_group': random.choice(self.resource_groups),
                'region': random.choice(self.regions),
                'status': random.choice(['Running', 'Stopped', 'Starting', 'Deallocated']),
                'tags': {
                    'environment': random.choice(['prod', 'dev', 'staging']),
                    'cost-center': f'cc-{random.randint(1000, 9999)}',
                    'owner': random.choice(['team-a', 'team-b', 'team-c'])
                },
                'created_date': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                'monthly_cost': random.randint(50, 2000)
            }
            resources.append(resource)
        
        # Apply filters
        if resource_group and resource_group != "All":
            resources = [r for r in resources if r['resource_group'] == resource_group]
        
        if resource_type and resource_type != "All":
            resources = [r for r in resources if r['type'] == resource_type]
        
        if region and region != "All":
            resources = [r for r in resources if r['region'] == region]
        
        return resources
    
    def get_cost_data(self, days: int = 30) -> Dict[str, Any]:
        """
        Get cost management data for specified time period.
        
        Args:
            days: Number of days to retrieve data for
            
        Returns:
            Dictionary with cost data and trends
        """
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=days),
            end=datetime.now(),
            freq='D'
        )
        
        # Generate realistic cost data with some trends
        base_cost = 500
        daily_costs = []
        
        for i, date in enumerate(dates):
            # Add some seasonality and trends
            seasonal = 50 * np.sin(2 * np.pi * i / 7)  # Weekly pattern
            trend = i * 2  # Slight upward trend
            noise = np.random.normal(0, 50)  # Random variation
            
            daily_cost = max(100, base_cost + seasonal + trend + noise)
            daily_costs.append(daily_cost)
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'daily_costs': daily_costs,
            'total_cost': sum(daily_costs),
            'average_daily_cost': np.mean(daily_costs),
            'cost_by_service': {
                'Virtual Machines': sum(daily_costs) * 0.4,
                'Storage': sum(daily_costs) * 0.18,
                'App Services': sum(daily_costs) * 0.22,
                'SQL Database': sum(daily_costs) * 0.12,
                'Networking': sum(daily_costs) * 0.06,
                'Other': sum(daily_costs) * 0.02
            },
            'cost_by_resource_group': {
                'rg-production': sum(daily_costs) * 0.55,
                'rg-development': sum(daily_costs) * 0.21,
                'rg-staging': sum(daily_costs) * 0.12,
                'rg-shared': sum(daily_costs) * 0.08,
                'rg-backup': sum(daily_costs) * 0.04
            }
        }
    
    def get_performance_metrics(self, resource_id: str, 
                              metric_name: str, 
                              hours: int = 24) -> Dict[str, Any]:
        """
        Get performance metrics for a specific resource.
        
        Args:
            resource_id: Resource identifier
            metric_name: Name of the metric (CPU, Memory, etc.)
            hours: Number of hours of data to retrieve
            
        Returns:
            Dictionary with metric data points
        """
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(hours=hours),
            end=datetime.now(),
            freq='5T'  # 5-minute intervals
        )
        
        # Generate realistic metric data based on metric type
        if metric_name.lower() in ['cpu', 'cpu_usage', 'processor_time']:
            # CPU usage typically 0-100%
            base = 65
            values = [max(0, min(100, base + np.random.normal(0, 15) + 10 * np.sin(2 * np.pi * i / 288))) 
                     for i in range(len(timestamps))]
        
        elif metric_name.lower() in ['memory', 'memory_usage', 'available_memory']:
            # Memory usage typically 0-100%
            base = 70
            values = [max(0, min(100, base + np.random.normal(0, 10) + 5 * np.sin(2 * np.pi * i / 288))) 
                     for i in range(len(timestamps))]
        
        elif metric_name.lower() in ['response_time', 'latency']:
            # Response time in milliseconds
            base = 250
            values = [max(50, base + np.random.normal(0, 50) + 20 * np.sin(2 * np.pi * i / 144)) 
                     for i in range(len(timestamps))]
        
        elif metric_name.lower() in ['requests', 'request_count']:
            # Request count per minute
            base = 1200
            values = [max(0, base + np.random.normal(0, 200) + 400 * np.sin(2 * np.pi * i / 288)) 
                     for i in range(len(timestamps))]
        
        else:
            # Generic metric
            base = 50
            values = [base + np.random.normal(0, 10) for _ in range(len(timestamps))]
        
        return {
            'resource_id': resource_id,
            'metric_name': metric_name,
            'timestamps': [t.isoformat() for t in timestamps],
            'values': values,
            'unit': self._get_metric_unit(metric_name),
            'aggregation': 'Average'
        }
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """Get appropriate unit for a metric."""
        metric_units = {
            'cpu': 'Percent',
            'cpu_usage': 'Percent',
            'processor_time': 'Percent',
            'memory': 'Percent',
            'memory_usage': 'Percent',
            'available_memory': 'Bytes',
            'response_time': 'Milliseconds',
            'latency': 'Milliseconds',
            'requests': 'Count',
            'request_count': 'Count/Minute',
            'disk_io': 'Bytes/Second',
            'network_in': 'Bytes/Second',
            'network_out': 'Bytes/Second'
        }
        
        return metric_units.get(metric_name.lower(), 'Count')
    
    def get_service_health(self) -> List[Dict[str, Any]]:
        """Get Azure service health status."""
        services = [
            'Virtual Machines',
            'Storage Accounts', 
            'App Services',
            'SQL Database',
            'Key Vault',
            'Container Instances',
            'Kubernetes Service',
            'Function Apps'
        ]
        
        health_status = []
        for service in services:
            status = {
                'service': service,
                'status': random.choice(['Healthy', 'Warning', 'Critical', 'Unknown']),
                'region': random.choice(self.regions),
                'last_updated': (datetime.now() - timedelta(minutes=random.randint(1, 30))).isoformat(),
                'issues': []
            }
            
            # Add some issues for non-healthy services
            if status['status'] in ['Warning', 'Critical']:
                issues = [
                    'High latency detected',
                    'Intermittent connectivity issues',
                    'Elevated error rates',
                    'Resource capacity constraints',
                    'Performance degradation'
                ]
                status['issues'] = random.sample(issues, random.randint(1, 2))
            
            health_status.append(status)
        
        return health_status
    
    def get_resource_utilization(self, resource_group: Optional[str] = None) -> Dict[str, Any]:
        """Get resource utilization summary."""
        resources = self.get_resources(resource_group=resource_group)
        
        # Calculate utilization stats
        total_resources = len(resources)
        running_resources = len([r for r in resources if r['status'] == 'Running'])
        stopped_resources = len([r for r in resources if r['status'] == 'Stopped'])
        
        utilization = {
            'total_resources': total_resources,
            'running_resources': running_resources,
            'stopped_resources': stopped_resources,
            'utilization_percentage': (running_resources / total_resources * 100) if total_resources > 0 else 0,
            'cost_optimization_opportunities': [
                {
                    'type': 'Right-size VMs',
                    'potential_savings': '$1,200/month',
                    'affected_resources': 12
                },
                {
                    'type': 'Unused resources',
                    'potential_savings': '$800/month', 
                    'affected_resources': 5
                },
                {
                    'type': 'Storage tier optimization',
                    'potential_savings': '$400/month',
                    'affected_resources': 8
                }
            ]
        }
        
        return utilization
    
    def execute_action(self, action: str, resource_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute an action on an Azure resource.
        
        Args:
            action: Action to perform (start, stop, restart, etc.)
            resource_id: Target resource identifier
            parameters: Additional parameters for the action
            
        Returns:
            Dictionary with action result
        """
        # Simulate action execution
        success_rate = 0.9  # 90% success rate for simulation
        success = random.random() < success_rate
        
        result = {
            'action': action,
            'resource_id': resource_id,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'execution_time': f"{random.uniform(0.5, 5.0):.1f} seconds"
        }
        
        if success:
            result['message'] = f"Action '{action}' completed successfully"
            result['status'] = 'Completed'
        else:
            result['message'] = f"Action '{action}' failed"
            result['error'] = random.choice([
                'Resource not found',
                'Insufficient permissions',
                'Resource is in invalid state',
                'Timeout occurred',
                'Service temporarily unavailable'
            ])
            result['status'] = 'Failed'
        
        return result
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get Azure Advisor recommendations."""
        recommendations = [
            {
                'category': 'Cost',
                'title': 'Right-size underutilized virtual machines',
                'description': 'Your virtual machines are underutilized. Consider resizing to a smaller SKU.',
                'potential_savings': '$1,200/month',
                'affected_resources': 12,
                'priority': 'High',
                'effort': 'Low'
            },
            {
                'category': 'Performance', 
                'title': 'Enable Accelerated Networking',
                'description': 'Improve network performance by enabling accelerated networking.',
                'potential_savings': 'Performance improvement',
                'affected_resources': 8,
                'priority': 'Medium',
                'effort': 'Low'
            },
            {
                'category': 'Security',
                'title': 'Enable Azure Security Center recommendations',
                'description': 'Apply security recommendations to improve your security posture.',
                'potential_savings': 'Security improvement',
                'affected_resources': 15,
                'priority': 'High', 
                'effort': 'Medium'
            },
            {
                'category': 'Reliability',
                'title': 'Configure backup for virtual machines',
                'description': 'Protect your virtual machines by configuring backup.',
                'potential_savings': 'Reliability improvement',
                'affected_resources': 6,
                'priority': 'Medium',
                'effort': 'Low'
            }
        ]
        
        return recommendations
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Azure connection and return status."""
        # Simulate connection test
        success = random.random() < 0.95  # 95% success rate
        
        if success:
            return {
                'connected': True,
                'message': 'Successfully connected to Azure',
                'subscriptions_found': len(self.subscriptions),
                'test_timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'connected': False,
                'message': 'Failed to connect to Azure',
                'error': random.choice([
                    'Invalid credentials',
                    'Network timeout',
                    'Service unavailable',
                    'Insufficient permissions'
                ]),
                'test_timestamp': datetime.now().isoformat()
            }
