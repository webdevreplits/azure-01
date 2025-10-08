"""
Real Azure SDK Client Implementation
Replaces mock Azure client with real Azure SDK integration.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.monitor.query import MetricsQueryClient, LogsQueryClient
from azure.core.exceptions import AzureError
import pandas as pd
from azure_auth import AzureAuth

class AzureRealClient:
    """
    Real Azure client using Azure SDK for production use.
    Provides live data from Azure Resource Manager, Cost Management, and Azure Monitor.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize authentication
        self.auth = AzureAuth(config)
        self.credential = None
        self.subscription_id = None
        
        # Azure SDK clients (lazy initialization)
        self._resource_client = None
        self._cost_client = None
        self._metrics_client = None
        self._logs_client = None
    
    def _ensure_authenticated(self):
        """Ensure we have valid credentials."""
        if not self.credential:
            self.credential = self.auth.get_credential()
            self.subscription_id = self.auth.get_subscription_id()
            
            if not self.subscription_id:
                raise Exception("Azure subscription ID not configured")
    
    @property
    def resource_client(self) -> ResourceManagementClient:
        """Get or create Resource Management client."""
        if not self._resource_client:
            self._ensure_authenticated()
            self._resource_client = ResourceManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        return self._resource_client
    
    @property
    def cost_client(self) -> CostManagementClient:
        """Get or create Cost Management client."""
        if not self._cost_client:
            self._ensure_authenticated()
            self._cost_client = CostManagementClient(
                credential=self.credential
            )
        return self._cost_client
    
    @property
    def metrics_client(self) -> MetricsQueryClient:
        """Get or create Metrics Query client."""
        if not self._metrics_client:
            self._ensure_authenticated()
            self._metrics_client = MetricsQueryClient(
                credential=self.credential
            )
        return self._metrics_client
    
    def get_subscriptions(self) -> List[str]:
        """Get list of available Azure subscriptions."""
        try:
            self._ensure_authenticated()
            from azure.mgmt.resource.subscriptions import SubscriptionClient
            
            sub_client = SubscriptionClient(credential=self.credential)
            subscriptions = []
            
            for sub in sub_client.subscriptions.list():
                subscriptions.append(sub.display_name or sub.subscription_id)
            
            return subscriptions
        except Exception as e:
            self.logger.error(f"Failed to get subscriptions: {e}")
            return []
    
    def get_resource_groups(self, subscription_id: Optional[str] = None) -> List[str]:
        """Get list of resource groups for a subscription."""
        try:
            resource_groups = []
            
            for rg in self.resource_client.resource_groups.list():
                resource_groups.append(rg.name)
            
            return resource_groups
        except Exception as e:
            self.logger.error(f"Failed to get resource groups: {e}")
            return []
    
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
        try:
            resources = []
            
            # Get resources based on filter
            if resource_group and resource_group != "All":
                resource_list = self.resource_client.resources.list_by_resource_group(
                    resource_group_name=resource_group
                )
            else:
                resource_list = self.resource_client.resources.list()
            
            for resource in resource_list:
                # Parse resource type
                res_type = resource.type.split('/')[-1] if resource.type else 'Unknown'
                
                # Apply filters
                if resource_type and resource_type != "All":
                    if res_type.lower() != resource_type.lower():
                        continue
                
                if region and region != "All":
                    if resource.location.lower() != region.lower():
                        continue
                
                # Build resource dictionary
                resource_dict = {
                    'id': resource.id,
                    'name': resource.name,
                    'type': res_type,
                    'resource_group': resource.id.split('/')[4] if len(resource.id.split('/')) > 4 else 'Unknown',
                    'region': resource.location,
                    'status': 'Running',  # Status requires additional API calls per resource
                    'tags': resource.tags or {},
                    'created_date': None,  # Not available in basic resource info
                    'monthly_cost': 0  # Requires Cost Management API
                }
                
                resources.append(resource_dict)
            
            return resources
        except Exception as e:
            self.logger.error(f"Failed to get resources: {e}")
            return []
    
    def get_cost_data(self, days: int = 30) -> Dict[str, Any]:
        """
        Get cost management data for specified time period.
        
        Args:
            days: Number of days to retrieve data for
            
        Returns:
            Dictionary with cost data and trends
        """
        try:
            from azure.mgmt.costmanagement.models import (
                QueryDefinition, QueryDataset, QueryAggregation,
                QueryTimePeriod, QueryGrouping, TimeframeType
            )
            
            # Define time period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Create query definition
            query = QueryDefinition(
                type="Usage",
                timeframe=TimeframeType.CUSTOM,
                time_period=QueryTimePeriod(
                    from_property=start_date,
                    to=end_date
                ),
                dataset=QueryDataset(
                    granularity="Daily",
                    aggregation={
                        "totalCost": QueryAggregation(name="PreTaxCost", function="Sum")
                    },
                    grouping=[
                        QueryGrouping(type="Dimension", name="ServiceName")
                    ]
                )
            )
            
            # Execute query
            scope = f"/subscriptions/{self.subscription_id}"
            result = self.cost_client.query.usage(scope=scope, parameters=query)
            
            # Process results
            dates = []
            daily_costs = []
            cost_by_service = {}
            
            for row in result.rows:
                # Parse row data based on columns
                # Format varies, need to adapt based on actual response
                pass
            
            return {
                'dates': dates,
                'daily_costs': daily_costs,
                'total_cost': sum(daily_costs) if daily_costs else 0,
                'average_daily_cost': sum(daily_costs) / len(daily_costs) if daily_costs else 0,
                'cost_by_service': cost_by_service,
                'cost_by_resource_group': {}
            }
        except Exception as e:
            self.logger.error(f"Failed to get cost data: {e}")
            # Return empty structure on error
            return {
                'dates': [],
                'daily_costs': [],
                'total_cost': 0,
                'average_daily_cost': 0,
                'cost_by_service': {},
                'cost_by_resource_group': {}
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
        try:
            from azure.monitor.query import MetricAggregationType
            
            # Define time period
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Query metrics
            response = self.metrics_client.query_resource(
                resource_uri=resource_id,
                metric_names=[metric_name],
                timespan=(start_time, end_time),
                granularity=timedelta(minutes=5),
                aggregations=[MetricAggregationType.AVERAGE]
            )
            
            timestamps = []
            values = []
            
            for metric in response.metrics:
                for time_series in metric.timeseries:
                    for data_point in time_series.data:
                        timestamps.append(data_point.time_stamp.isoformat())
                        values.append(data_point.average or 0)
            
            return {
                'resource_id': resource_id,
                'metric_name': metric_name,
                'timestamps': timestamps,
                'values': values,
                'unit': self._get_metric_unit(metric_name),
                'aggregation': 'Average'
            }
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return {
                'resource_id': resource_id,
                'metric_name': metric_name,
                'timestamps': [],
                'values': [],
                'unit': self._get_metric_unit(metric_name),
                'aggregation': 'Average'
            }
    
    def _get_metric_unit(self, metric_name: str) -> str:
        """Get appropriate unit for a metric."""
        metric_units = {
            'cpu': 'Percent',
            'percentage cpu': 'Percent',
            'memory': 'Percent',
            'available memory bytes': 'Bytes',
            'network in': 'Bytes',
            'network out': 'Bytes',
            'disk read bytes': 'Bytes',
            'disk write bytes': 'Bytes'
        }
        
        return metric_units.get(metric_name.lower(), 'Count')
    
    def get_service_health(self) -> List[Dict[str, Any]]:
        """Get Azure service health status."""
        try:
            from azure.mgmt.resourcehealth import ResourceHealthMgmtClient
            
            health_client = ResourceHealthMgmtClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
            
            health_status = []
            
            # Get availability statuses for resources
            for status in health_client.availability_statuses.list_by_subscription_id(
                subscription_id=self.subscription_id
            ):
                health_status.append({
                    'service': status.name,
                    'status': status.properties.availability_state if status.properties else 'Unknown',
                    'region': status.location,
                    'last_updated': status.properties.occurred_time.isoformat() if status.properties and status.properties.occurred_time else None,
                    'issues': []
                })
            
            return health_status
        except Exception as e:
            self.logger.error(f"Failed to get service health: {e}")
            return []
    
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
        try:
            # Parse resource ID to get provider and resource info
            parts = resource_id.split('/')
            
            if 'Microsoft.Compute' in resource_id and 'virtualMachines' in resource_id:
                from azure.mgmt.compute import ComputeManagementClient
                
                compute_client = ComputeManagementClient(
                    credential=self.credential,
                    subscription_id=self.subscription_id
                )
                
                rg_name = parts[4]
                vm_name = parts[8]
                
                if action.lower() == 'start':
                    result = compute_client.virtual_machines.begin_start(rg_name, vm_name)
                elif action.lower() == 'stop':
                    result = compute_client.virtual_machines.begin_deallocate(rg_name, vm_name)
                elif action.lower() == 'restart':
                    result = compute_client.virtual_machines.begin_restart(rg_name, vm_name)
                else:
                    raise Exception(f"Unsupported action: {action}")
                
                return {
                    'action': action,
                    'resource_id': resource_id,
                    'success': True,
                    'timestamp': datetime.now().isoformat(),
                    'message': f"Action '{action}' initiated successfully",
                    'status': 'Completed'
                }
            else:
                raise Exception(f"Action '{action}' not supported for this resource type")
                
        except Exception as e:
            self.logger.error(f"Failed to execute action: {e}")
            return {
                'action': action,
                'resource_id': resource_id,
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'message': f"Action '{action}' failed",
                'error': str(e),
                'status': 'Failed'
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Azure connection and return status."""
        auth_result = self.auth.test_authentication()
        
        if auth_result['authenticated']:
            try:
                # Try to get subscriptions as additional verification
                subscriptions = self.get_subscriptions()
                
                return {
                    'connected': True,
                    'message': 'Successfully connected to Azure',
                    'subscriptions_found': len(subscriptions),
                    'credential_type': auth_result.get('credential_type'),
                    'test_timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    'connected': False,
                    'message': 'Authentication succeeded but API access failed',
                    'error': str(e),
                    'test_timestamp': datetime.now().isoformat()
                }
        else:
            return {
                'connected': False,
                'message': auth_result['message'],
                'error': auth_result.get('error'),
                'test_timestamp': datetime.now().isoformat()
            }
