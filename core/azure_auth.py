"""
Azure Authentication Module
Handles Azure authentication using DefaultAzureCredential with fallback options.
"""

import os
import logging
from typing import Optional, Dict, Any
from azure.identity import DefaultAzureCredential, ClientSecretCredential, ManagedIdentityCredential
from azure.core.credentials import AccessToken

class AzureAuth:
    """
    Azure authentication manager supporting multiple authentication methods:
    - DefaultAzureCredential (recommended for most scenarios)
    - Service Principal (client_id + client_secret + tenant_id)
    - Managed Identity (for Azure resources)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.credential = None
        self.logger = logging.getLogger(__name__)
        
    def get_credential(self):
        """
        Get Azure credential for authentication.
        
        Returns:
            Azure credential object
        """
        if self.credential:
            return self.credential
        
        # Try to get credentials from config or environment
        auth_config = self.config.get('azure_auth', {})
        
        # Option 1: Service Principal (explicit credentials)
        if all(key in auth_config for key in ['tenant_id', 'client_id', 'client_secret']):
            try:
                self.logger.info("Using Service Principal authentication")
                self.credential = ClientSecretCredential(
                    tenant_id=auth_config['tenant_id'],
                    client_id=auth_config['client_id'],
                    client_secret=auth_config['client_secret']
                )
                return self.credential
            except Exception as e:
                self.logger.error(f"Service Principal authentication failed: {e}")
        
        # Option 2: Managed Identity (for Azure-hosted resources)
        if auth_config.get('use_managed_identity', False):
            try:
                self.logger.info("Using Managed Identity authentication")
                client_id = auth_config.get('managed_identity_client_id')
                self.credential = ManagedIdentityCredential(client_id=client_id)
                return self.credential
            except Exception as e:
                self.logger.error(f"Managed Identity authentication failed: {e}")
        
        # Option 3: DefaultAzureCredential (tries multiple methods)
        try:
            self.logger.info("Using DefaultAzureCredential authentication")
            # DefaultAzureCredential tries these in order:
            # 1. EnvironmentCredential
            # 2. ManagedIdentityCredential
            # 3. SharedTokenCacheCredential
            # 4. VisualStudioCodeCredential
            # 5. AzureCliCredential
            # 6. AzurePowerShellCredential
            self.credential = DefaultAzureCredential()
            return self.credential
        except Exception as e:
            self.logger.error(f"DefaultAzureCredential failed: {e}")
            raise Exception("Failed to authenticate with Azure. Please configure credentials.")
    
    def test_authentication(self) -> Dict[str, Any]:
        """
        Test Azure authentication and return status.
        
        Returns:
            Dictionary with authentication status
        """
        try:
            credential = self.get_credential()
            
            # Try to get a token to verify authentication works
            # Using management scope as a test
            token = credential.get_token("https://management.azure.com/.default")
            
            return {
                'authenticated': True,
                'message': 'Successfully authenticated with Azure',
                'credential_type': type(credential).__name__,
                'token_expires': token.expires_on if hasattr(token, 'expires_on') else None
            }
        except Exception as e:
            self.logger.error(f"Authentication test failed: {e}")
            return {
                'authenticated': False,
                'message': 'Authentication failed',
                'error': str(e),
                'credential_type': None
            }
    
    def get_subscription_id(self) -> Optional[str]:
        """
        Get Azure subscription ID from config or environment.
        
        Returns:
            Subscription ID string or None
        """
        # Try config first
        sub_id = self.config.get('azure_auth', {}).get('subscription_id')
        
        # Try environment variables
        if not sub_id:
            sub_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
        
        return sub_id
    
    def is_configured(self) -> bool:
        """
        Check if Azure authentication is configured.
        
        Returns:
            True if configured, False otherwise
        """
        auth_config = self.config.get('azure_auth', {})
        
        # Check if we have explicit credentials
        if all(key in auth_config for key in ['tenant_id', 'client_id', 'client_secret']):
            return True
        
        # Check if managed identity is enabled
        if auth_config.get('use_managed_identity', False):
            return True
        
        # Check if Azure CLI is configured (for DefaultAzureCredential)
        if os.environ.get('AZURE_CLIENT_ID') or os.environ.get('AZURE_TENANT_ID'):
            return True
        
        return False
