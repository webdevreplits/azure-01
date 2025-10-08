"""
Azure Client Factory
Creates either mock or real Azure client based on configuration.
"""

from typing import Dict, Any
import logging

def create_azure_client(config: Dict[str, Any]):
    """
    Create Azure client instance based on configuration.
    
    Args:
        config: Application configuration dictionary
        
    Returns:
        Azure client instance (mock or real)
    """
    logger = logging.getLogger(__name__)
    
    # Check if we should use real Azure client
    use_real_client = config.get('azure', {}).get('use_real_client', False)
    
    # Check if Azure credentials are configured
    azure_auth_config = config.get('azure_auth', {})
    has_credentials = bool(
        azure_auth_config.get('tenant_id') or 
        azure_auth_config.get('subscription_id') or
        azure_auth_config.get('use_managed_identity')
    )
    
    if use_real_client and has_credentials:
        try:
            from .azure_real_client import AzureRealClient
            logger.info("Creating real Azure SDK client")
            return AzureRealClient(config)
        except ImportError as e:
            logger.warning(f"Failed to import real Azure client: {e}. Falling back to mock client.")
        except Exception as e:
            logger.warning(f"Failed to create real Azure client: {e}. Falling back to mock client.")
    
    # Default to mock client
    from .azure_client import AzureClient
    logger.info("Creating mock Azure client")
    return AzureClient()
