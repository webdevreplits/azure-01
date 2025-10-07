"""
Dynamic dependency installer for different environments.
Handles package installation for Replit, Databricks, and local environments.
"""

import os
import sys
import subprocess
import importlib
import logging
from typing import List, Dict, Any, Optional, Tuple

class DependencyInstaller:
    """
    Manages dynamic installation of dependencies based on environment.
    """
    
    def __init__(self, environment: str):
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        self.installed_packages = set()
        
    def check_and_install_dependencies(self, required_packages: List[str]) -> Dict[str, Any]:
        """
        Check for missing dependencies and install them.
        
        Args:
            required_packages: List of required package names
            
        Returns:
            Dictionary with installation results
        """
        results = {
            'environment': self.environment,
            'required_packages': required_packages,
            'missing_packages': [],
            'installation_results': {},
            'success': True,
            'errors': []
        }
        
        # Check which packages are missing
        missing_packages = []
        for package in required_packages:
            if not self._is_package_available(package):
                missing_packages.append(package)
        
        results['missing_packages'] = missing_packages
        
        if not missing_packages:
            self.logger.info("All required packages are already available")
            return results
        
        # Install missing packages
        self.logger.info(f"Installing {len(missing_packages)} missing packages: {missing_packages}")
        
        for package in missing_packages:
            install_result = self._install_package(package)
            results['installation_results'][package] = install_result
            
            if not install_result['success']:
                results['success'] = False
                results['errors'].append(f"Failed to install {package}: {install_result.get('error', 'Unknown error')}")
        
        return results
    
    def _is_package_available(self, package_name: str) -> bool:
        """
        Check if a package is available for import.
        
        Args:
            package_name: Name of the package to check
            
        Returns:
            True if package is available, False otherwise
        """
        # Handle package name mappings
        import_name = self._get_import_name(package_name)
        
        try:
            importlib.import_module(import_name)
            return True
        except ImportError:
            return False
    
    def _get_import_name(self, package_name: str) -> str:
        """
        Map package names to their import names.
        
        Args:
            package_name: Package name from pip
            
        Returns:
            Import name for the package
        """
        # Common package name mappings
        name_mappings = {
            'psycopg2-binary': 'psycopg2',
            'python-dotenv': 'dotenv',
            'pyyaml': 'yaml',
            'databricks-sql-connector': 'databricks.sql',
            'databricks-cli': 'databricks_cli',
            'streamlit-aggrid': 'st_aggrid',
            'pillow': 'PIL'
        }
        
        return name_mappings.get(package_name, package_name)
    
    def _install_package(self, package_name: str) -> Dict[str, Any]:
        """
        Install a single package using the appropriate method for the environment.
        
        Args:
            package_name: Name of the package to install
            
        Returns:
            Dictionary with installation result
        """
        result = {
            'package': package_name,
            'method': '',
            'success': False,
            'output': '',
            'error': ''
        }
        
        try:
            if self.environment == "databricks":
                result = self._install_databricks_package(package_name)
            else:
                result = self._install_pip_package(package_name)
            
            if result['success']:
                self.installed_packages.add(package_name)
                self.logger.info(f"Successfully installed {package_name}")
            else:
                self.logger.error(f"Failed to install {package_name}: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Exception while installing {package_name}: {e}")
        
        return result
    
    def _install_pip_package(self, package_name: str) -> Dict[str, Any]:
        """
        Install package using pip.
        
        Args:
            package_name: Package name to install
            
        Returns:
            Installation result dictionary
        """
        result = {
            'package': package_name,
            'method': 'pip',
            'success': False,
            'output': '',
            'error': ''
        }
        
        try:
            # Use subprocess to install package
            cmd = [sys.executable, '-m', 'pip', 'install', package_name]
            
            # Add quiet flag to reduce output
            cmd.append('-q')
            
            # For Replit, we might need --user flag
            if self.environment == "replit":
                cmd.append('--user')
            
            # Run installation command
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            
            if not result['success']:
                result['error'] = result['error'] or f"Installation failed with return code {process.returncode}"
        
        except subprocess.TimeoutExpired:
            result['error'] = "Installation timed out"
        except Exception as e:
            result['error'] = f"Installation exception: {str(e)}"
        
        return result
    
    def _install_databricks_package(self, package_name: str) -> Dict[str, Any]:
        """
        Install package in Databricks environment.
        
        Args:
            package_name: Package name to install
            
        Returns:
            Installation result dictionary
        """
        result = {
            'package': package_name,
            'method': 'databricks_pip',
            'success': False,
            'output': '',
            'error': ''
        }
        
        try:
            # In Databricks, we can use %pip install magic command
            # Since we're not in a notebook context, we'll use subprocess
            cmd = [sys.executable, '-m', 'pip', 'install', package_name]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            
        except Exception as e:
            result['error'] = f"Databricks installation exception: {str(e)}"
        
        return result
    
    def get_installation_summary(self) -> Dict[str, Any]:
        """
        Get summary of installed packages.
        
        Returns:
            Installation summary dictionary
        """
        return {
            'environment': self.environment,
            'installed_packages': list(self.installed_packages),
            'total_installed': len(self.installed_packages)
        }
    
    def verify_installations(self, packages: List[str]) -> Dict[str, bool]:
        """
        Verify that packages are properly installed.
        
        Args:
            packages: List of packages to verify
            
        Returns:
            Dictionary mapping package names to availability status
        """
        verification = {}
        
        for package in packages:
            verification[package] = self._is_package_available(package)
        
        return verification
    
    def get_package_info(self, package_name: str) -> Dict[str, Any]:
        """
        Get information about an installed package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            Package information dictionary
        """
        info = {
            'package': package_name,
            'available': False,
            'version': None,
            'location': None
        }
        
        try:
            import_name = self._get_import_name(package_name)
            module = importlib.import_module(import_name)
            
            info['available'] = True
            
            # Try to get version
            if hasattr(module, '__version__'):
                info['version'] = module.__version__
            elif hasattr(module, 'VERSION'):
                info['version'] = module.VERSION
            
            # Try to get location
            if hasattr(module, '__file__'):
                info['location'] = os.path.dirname(module.__file__)
        
        except ImportError:
            pass
        except Exception as e:
            info['error'] = str(e)
        
        return info

def check_and_install_dependencies(environment: str, required_packages: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convenience function to check and install dependencies.
    
    Args:
        environment: Environment type (replit, databricks, local)
        required_packages: List of required packages (uses defaults if None)
        
    Returns:
        Installation results dictionary
    """
    if required_packages is None:
        # Default required packages
        required_packages = [
            'streamlit',
            'pandas',
            'plotly',
            'psycopg2-binary',
            'python-dotenv',
            'pyyaml'
        ]
        
        # Add environment-specific packages
        if environment == "databricks":
            required_packages.extend([
                'databricks-sql-connector'
            ])
    
    installer = DependencyInstaller(environment)
    return installer.check_and_install_dependencies(required_packages)

def install_missing_package(package_name: str, environment: str) -> bool:
    """
    Install a single missing package.
    
    Args:
        package_name: Name of the package to install
        environment: Environment type
        
    Returns:
        True if installation successful, False otherwise
    """
    installer = DependencyInstaller(environment)
    result = installer._install_package(package_name)
    return result['success']

def get_installed_packages() -> List[str]:
    """
    Get list of currently installed packages.
    
    Returns:
        List of installed package names
    """
    try:
        import pkg_resources
        return [pkg.project_name for pkg in pkg_resources.working_set]
    except ImportError:
        # Fallback method using subprocess
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'list', '--format=freeze'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                packages = []
                for line in result.stdout.split('\n'):
                    if '==' in line:
                        packages.append(line.split('==')[0])
                return packages
        except Exception:
            pass
        
        return []

def check_package_compatibility(package_name: str, python_version: str) -> Dict[str, Any]:
    """
    Check if a package is compatible with the current Python version.
    
    Args:
        package_name: Name of the package
        python_version: Python version string
        
    Returns:
        Compatibility information dictionary
    """
    # This is a simplified compatibility check
    # In production, you might want to query PyPI API for detailed compatibility
    
    compatibility = {
        'package': package_name,
        'python_version': python_version,
        'compatible': True,
        'warnings': []
    }
    
    # Known compatibility issues
    major_version = int(python_version.split('.')[0])
    minor_version = int(python_version.split('.')[1])
    
    if major_version < 3:
        compatibility['compatible'] = False
        compatibility['warnings'].append("Python 2 is not supported")
    
    if major_version == 3 and minor_version < 7:
        if package_name in ['streamlit']:
            compatibility['compatible'] = False
            compatibility['warnings'].append(f"{package_name} requires Python 3.7+")
    
    return compatibility
