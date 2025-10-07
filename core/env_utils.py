"""
Environment detection and utility functions.
Handles detection of Replit, Databricks, and local environments.
"""

import os
import sys
import platform
from typing import Dict, Any, Optional

def detect_environment() -> str:
    """
    Detect the current runtime environment.
    
    Returns:
        Environment string: 'replit', 'databricks', or 'local'
    """
    # Check for Replit environment
    if "REPL_ID" in os.environ or "REPL_SLUG" in os.environ:
        return "replit"
    
    # Check for Databricks environment
    if "DATABRICKS_RUNTIME_VERSION" in os.environ or "SPARK_HOME" in os.environ:
        return "databricks"
    
    # Check for other cloud environments
    if "CODESPACE_NAME" in os.environ:
        return "codespace"
    
    if "GITPOD_WORKSPACE_ID" in os.environ:
        return "gitpod"
    
    # Default to local
    return "local"

def get_environment_info(env_type: str) -> Dict[str, Any]:
    """
    Get detailed information about the current environment.
    
    Args:
        env_type: Environment type from detect_environment()
        
    Returns:
        Dictionary with environment details
    """
    base_info = {
        'type': env_type,
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'platform': platform.platform(),
        'architecture': platform.architecture()[0]
    }
    
    if env_type == "replit":
        return {
            **base_info,
            'name': 'Replit',
            'status': '🟢 Active',
            'version': os.getenv('REPL_LANGUAGE_VERSION', 'Unknown'),
            'detection_method': 'REPL_ID environment variable',
            'features': [
                'Built-in PostgreSQL database',
                'Automatic HTTPS',
                'Real-time collaboration',
                'Package management',
                'Secrets management'
            ],
            'limitations': [
                'Resource limits apply',
                'Always-on requires subscription',
                'Storage limitations'
            ],
            'config_path': os.getenv('REPL_HOME', '/home/runner'),
            'database_type': 'PostgreSQL (Managed)',
            'environment_variables': {
                'REPL_ID': os.getenv('REPL_ID'),
                'REPL_SLUG': os.getenv('REPL_SLUG'),
                'REPL_OWNER': os.getenv('REPL_OWNER')
            }
        }
    
    elif env_type == "databricks":
        return {
            **base_info,
            'name': 'Databricks',
            'status': '🔵 Active',
            'version': os.getenv('DATABRICKS_RUNTIME_VERSION', 'Unknown'),
            'detection_method': 'DATABRICKS_RUNTIME_VERSION environment variable',
            'features': [
                'Spark integration',
                'Databricks SQL Warehouse',
                'MLflow integration',
                'Delta Lake support',
                'Collaborative notebooks'
            ],
            'limitations': [
                'Cluster startup time',
                'Compute costs when running',
                'Session timeouts'
            ],
            'config_path': '/databricks/driver',
            'database_type': 'Databricks SQL',
            'cluster_info': {
                'cluster_id': os.getenv('DATABRICKS_CLUSTER_ID'),
                'spark_version': os.getenv('SPARK_VERSION'),
                'node_type': os.getenv('DATABRICKS_NODE_TYPE')
            }
        }
    
    elif env_type == "codespace":
        return {
            **base_info,
            'name': 'GitHub Codespace',
            'status': '🟢 Active',
            'version': 'Latest',
            'detection_method': 'CODESPACE_NAME environment variable',
            'features': [
                'VS Code in browser',
                'GitHub integration',
                'Port forwarding',
                'Extensions support'
            ],
            'limitations': [
                'Usage quotas apply',
                'Automatic shutdown',
                'Storage limitations'
            ],
            'config_path': '/workspaces',
            'database_type': 'SQLite (default)'
        }
    
    elif env_type == "gitpod":
        return {
            **base_info,
            'name': 'Gitpod',
            'status': '🟢 Active', 
            'version': 'Latest',
            'detection_method': 'GITPOD_WORKSPACE_ID environment variable',
            'features': [
                'VS Code or Theia',
                'Git integration',
                'Prebuilds support',
                'Port forwarding'
            ],
            'limitations': [
                'Workspace timeout',
                'Storage limitations',
                'Usage quotas'
            ],
            'config_path': '/workspace',
            'database_type': 'SQLite (default)'
        }
    
    else:  # local
        return {
            **base_info,
            'name': 'Local Development',
            'status': '🟡 Local',
            'version': 'Custom',
            'detection_method': 'Default (no cloud indicators)',
            'features': [
                'Full system access',
                'Custom database setup',
                'Development tools',
                'No usage limits'
            ],
            'limitations': [
                'Manual configuration required',
                'No automatic scaling',
                'Local network only'
            ],
            'config_path': os.getcwd(),
            'database_type': 'PostgreSQL or SQLite'
        }

def get_database_config(env_type: str) -> Dict[str, Any]:
    """
    Get database configuration based on environment.
    
    Args:
        env_type: Environment type
        
    Returns:
        Database configuration dictionary
    """
    if env_type == "replit":
        # Replit provides managed PostgreSQL
        return {
            'type': 'postgresql',
            'host': os.getenv('PGHOST'),
            'port': int(os.getenv('PGPORT', '5432')),
            'database': os.getenv('PGDATABASE'),
            'username': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD'),
            'url': os.getenv('DATABASE_URL'),
            'ssl_mode': 'require',
            'managed': True
        }
    
    elif env_type == "databricks":
        # Databricks SQL Warehouse
        return {
            'type': 'databricks_sql',
            'server_hostname': os.getenv('DATABRICKS_SERVER_HOSTNAME'),
            'http_path': os.getenv('DATABRICKS_HTTP_PATH'),
            'access_token': os.getenv('DATABRICKS_ACCESS_TOKEN'),
            'managed': True
        }
    
    else:
        # Local or other - try PostgreSQL, fallback to SQLite
        return {
            'type': 'postgresql',
            'host': os.getenv('PGHOST', 'localhost'),
            'port': int(os.getenv('PGPORT', '5432')),
            'database': os.getenv('PGDATABASE', 'azure_support'),
            'username': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', ''),
            'url': os.getenv('DATABASE_URL', ''),
            'fallback_to_sqlite': True,
            'managed': False
        }

def get_required_packages(env_type: str) -> list:
    """
    Get list of required packages for the environment.
    
    Args:
        env_type: Environment type
        
    Returns:
        List of package names
    """
    base_packages = [
        'streamlit',
        'pandas',
        'plotly', 
        'psycopg2-binary',
        'python-dotenv',
        'pyyaml'
    ]
    
    if env_type == "databricks":
        # Databricks-specific packages
        base_packages.extend([
            'databricks-sql-connector',
            'databricks-cli'
        ])
    
    elif env_type == "replit":
        # Replit usually has most packages available
        pass
    
    return base_packages

def setup_environment_paths(env_type: str) -> Dict[str, str]:
    """
    Set up environment-specific paths.
    
    Args:
        env_type: Environment type
        
    Returns:
        Dictionary of path configurations
    """
    paths = {
        'home': os.path.expanduser('~'),
        'current': os.getcwd(),
        'data': os.path.join(os.getcwd(), 'data'),
        'logs': os.path.join(os.getcwd(), 'logs'),
        'config': os.path.join(os.getcwd(), 'config')
    }
    
    if env_type == "replit":
        paths.update({
            'home': os.getenv('REPL_HOME', '/home/runner'),
            'data': os.path.join(os.getenv('REPL_HOME', '/home/runner'), 'data'),
            'logs': os.path.join(os.getenv('REPL_HOME', '/home/runner'), 'logs')
        })
    
    elif env_type == "databricks":
        paths.update({
            'home': '/databricks/driver',
            'data': '/tmp/azure_support_data',
            'logs': '/tmp/azure_support_logs'
        })
    
    # Create directories if they don't exist
    for path_name, path_value in paths.items():
        if path_name != 'home' and path_name != 'current':
            try:
                os.makedirs(path_value, exist_ok=True)
            except (OSError, PermissionError):
                # Use current directory as fallback
                paths[path_name] = os.getcwd()
    
    return paths

def check_environment_requirements(env_type: str) -> Dict[str, Any]:
    """
    Check if environment meets requirements.
    
    Args:
        env_type: Environment type
        
    Returns:
        Dictionary with requirement check results
    """
    checks = {
        'python_version': {
            'required': '3.8+',
            'current': f"{sys.version_info.major}.{sys.version_info.minor}",
            'passed': sys.version_info >= (3, 8)
        },
        'environment_variables': {
            'required': [],
            'missing': [],
            'passed': True
        },
        'network_access': {
            'required': True,
            'passed': True  # Assume available for now
        }
    }
    
    # Environment-specific checks
    if env_type == "replit":
        required_vars = ['PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        checks['environment_variables'].update({
            'required': required_vars,
            'missing': missing_vars,
            'passed': len(missing_vars) == 0
        })
    
    elif env_type == "databricks":
        required_vars = ['DATABRICKS_RUNTIME_VERSION']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        checks['environment_variables'].update({
            'required': required_vars,
            'missing': missing_vars,
            'passed': len(missing_vars) == 0
        })
    
    # Overall status
    checks['overall_passed'] = all(
        check.get('passed', True) for check in checks.values() 
        if isinstance(check, dict) and 'passed' in check
    )
    
    return checks

def get_environment_secrets() -> Dict[str, Optional[str]]:
    """
    Get environment secrets/credentials safely.
    
    Returns:
        Dictionary of available secrets (values are masked)
    """
    secret_keys = [
        'DATABASE_URL',
        'PGPASSWORD', 
        'SESSION_SECRET',
        'AZURE_CLIENT_SECRET',
        'AZURE_CLIENT_ID',
        'AZURE_TENANT_ID',
        'DATABRICKS_ACCESS_TOKEN'
    ]
    
    secrets = {}
    for key in secret_keys:
        value = os.getenv(key)
        if value:
            # Mask the value for security
            if len(value) > 8:
                secrets[key] = f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"
            else:
                secrets[key] = "*" * len(value)
        else:
            secrets[key] = None
    
    return secrets

def is_development_mode() -> bool:
    """
    Check if running in development mode.
    
    Returns:
        True if in development mode
    """
    return (
        os.getenv('DEBUG', '').lower() == 'true' or
        os.getenv('ENVIRONMENT', '').lower() == 'development' or
        detect_environment() == 'local'
    )

def get_streamlit_config(env_type: str) -> Dict[str, Any]:
    """
    Get Streamlit configuration based on environment.
    
    Args:
        env_type: Environment type
        
    Returns:
        Streamlit configuration dictionary
    """
    config = {
        'server': {
            'headless': True,
            'address': '0.0.0.0',
            'port': 5000,
            'enableCORS': False,
            'enableXsrfProtection': False
        },
        'browser': {
            'gatherUsageStats': False,
            'serverAddress': '0.0.0.0',
            'serverPort': 5000
        }
    }
    
    # Environment-specific adjustments
    if env_type == "replit":
        config['server'].update({
            'enableWebsocketCompression': True,
            'runOnSave': True
        })
    
    elif env_type == "databricks":
        config['server'].update({
            'enableWebsocketCompression': False,
            'maxUploadSize': 200
        })
    
    return config
