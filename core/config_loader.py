import os
import json
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv

def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables and config files.
    Priority: Environment variables > config.yaml > .env > defaults
    """
    # Load .env file if it exists
    load_dotenv()
    
    config = {
        'database': {
            'host': os.getenv('PGHOST', 'localhost'),
            'port': int(os.getenv('PGPORT', '5432')),
            'database': os.getenv('PGDATABASE', 'azure_support'),
            'username': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', ''),
            'url': os.getenv('DATABASE_URL', '')
        },
        'azure': {
            'tenant_id': os.getenv('AZURE_TENANT_ID', ''),
            'client_id': os.getenv('AZURE_CLIENT_ID', ''),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET', ''),
            'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID', ''),
        },
        'app': {
            'debug': os.getenv('DEBUG', 'False').lower() == 'true',
            'host': os.getenv('HOST', '0.0.0.0'),
            'port': int(os.getenv('PORT', '5000')),
            'secret_key': os.getenv('SESSION_SECRET', 'dev-secret-key'),
            'auto_refresh': os.getenv('AUTO_REFRESH', 'True').lower() == 'true',
            'refresh_interval': int(os.getenv('REFRESH_INTERVAL', '30'))
        },
        'features': {
            'enable_cost_management': os.getenv('ENABLE_COST_MANAGEMENT', 'True').lower() == 'true',
            'enable_performance_monitor': os.getenv('ENABLE_PERFORMANCE_MONITOR', 'True').lower() == 'true',
            'enable_automation': os.getenv('ENABLE_AUTOMATION', 'True').lower() == 'true',
            'enable_debug_mode': os.getenv('ENABLE_DEBUG_MODE', 'False').lower() == 'true'
        }
    }
    
    # Try to load config.yaml if it exists
    try:
        if os.path.exists('config.yaml'):
            with open('config.yaml', 'r') as f:
                yaml_config = yaml.safe_load(f)
                # Merge with existing config, giving priority to yaml
                config = merge_configs(config, yaml_config)
    except Exception as e:
        print(f"Warning: Could not load config.yaml: {e}")
    
    # Try to load config.json if it exists
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                json_config = json.load(f)
                # Merge with existing config, giving priority to json
                config = merge_configs(config, json_config)
    except Exception as e:
        print(f"Warning: Could not load config.json: {e}")
    
    return config

def save_config(config: Dict[str, Any], format: str = 'yaml') -> bool:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        format: 'yaml' or 'json'
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if format.lower() == 'yaml':
            with open('config.yaml', 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        elif format.lower() == 'json':
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries, with override taking precedence.
    
    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary
    
    Returns:
        Merged configuration dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result

def get_database_url(config: Dict[str, Any]) -> str:
    """
    Build database URL from configuration.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Database URL string
    """
    db_config = config.get('database', {})
    
    # If DATABASE_URL is provided, use it directly
    if db_config.get('url'):
        return db_config['url']
    
    # Build URL from components
    host = db_config.get('host', 'localhost')
    port = db_config.get('port', 5432)
    database = db_config.get('database', 'azure_support')
    username = db_config.get('username', 'postgres')
    password = db_config.get('password', '')
    
    if password:
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    else:
        return f"postgresql://{username}@{host}:{port}/{database}"

def validate_config(config: Dict[str, Any]) -> tuple[bool, list]:
    """
    Validate configuration for required fields and correct formats.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Validate database config
    db_config = config.get('database', {})
    if not db_config.get('host') and not db_config.get('url'):
        errors.append("Database host or URL is required")
    
    # Validate app config
    app_config = config.get('app', {})
    try:
        port = int(app_config.get('port', 5000))
        if port < 1 or port > 65535:
            errors.append("App port must be between 1 and 65535")
    except (ValueError, TypeError):
        errors.append("App port must be a valid integer")
    
    # Validate Azure config (optional, but if provided should be complete)
    azure_config = config.get('azure', {})
    if azure_config.get('tenant_id') or azure_config.get('client_id'):
        required_azure_fields = ['tenant_id', 'client_id', 'client_secret']
        for field in required_azure_fields:
            if not azure_config.get(field):
                errors.append(f"Azure {field} is required when using Service Principal auth")
    
    return len(errors) == 0, errors

def get_config_summary(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Get a safe summary of configuration (no sensitive data).
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Summary dictionary with safe values
    """
    summary = {
        'database_host': config.get('database', {}).get('host', 'Not configured'),
        'database_name': config.get('database', {}).get('database', 'Not configured'),
        'app_port': str(config.get('app', {}).get('port', 'Not configured')),
        'debug_mode': str(config.get('app', {}).get('debug', False)),
        'auto_refresh': str(config.get('app', {}).get('auto_refresh', True)),
        'azure_configured': 'Yes' if config.get('azure', {}).get('tenant_id') else 'No',
        'features_enabled': str(len([k for k, v in config.get('features', {}).items() if v]))
    }
    
    return summary
