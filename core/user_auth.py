"""
User Authentication and Role-Based Access Control (RBAC)
Simple authentication system for the Azure Platform Support app.
"""

import hashlib
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime
from db_manager import DatabaseManager

class UserAuth:
    """
    User authentication and authorization manager.
    Supports role-based access control (RBAC).
    """
    
    ROLES = {
        'Admin': {
            'permissions': ['read', 'write', 'delete', 'admin'],
            'description': 'Full system access including user management'
        },
        'Engineer': {
            'permissions': ['read', 'write'],
            'description': 'Can view and modify resources, manage incidents'
        },
        'Viewer': {
            'permissions': ['read'],
            'description': 'Read-only access to all features'
        }
    }
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Hash a password with a salt.
        
        Args:
            password: Plain text password
            salt: Optional salt (will be generated if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if not salt:
            salt = secrets.token_hex(16)
        
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        
        return pwd_hash.hex(), salt
    
    def create_user(self, username: str, password: str, email: str, role: str = 'Viewer') -> bool:
        """
        Create a new user account.
        
        Args:
            username: Unique username
            password: User password
            email: User email
            role: User role (Admin, Engineer, Viewer)
            
        Returns:
            True if successful, False otherwise
        """
        if role not in self.ROLES:
            raise ValueError(f"Invalid role: {role}. Must be one of {list(self.ROLES.keys())}")
        
        # Hash password
        pwd_hash, salt = self.hash_password(password)
        
        # Create user record
        if self.db_manager.db_type == 'postgresql':
            query = """
                INSERT INTO users (username, password_hash, password_salt, email, role, created_at)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
        else:
            query = """
                INSERT INTO users (username, password_hash, password_salt, email, role, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
        
        return self.db_manager.execute_update(query, (username, pwd_hash, salt, email, role))
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User dictionary if successful, None otherwise
        """
        # Get user from database
        if self.db_manager.db_type == 'postgresql':
            query = "SELECT * FROM users WHERE username = %s"
        else:
            query = "SELECT * FROM users WHERE username = ?"
        
        results = self.db_manager.execute_query(query, (username,))
        
        if not results:
            return None
        
        user = results[0]
        
        # Verify password
        pwd_hash, _ = self.hash_password(password, user.get('password_salt'))
        
        if pwd_hash == user.get('password_hash'):
            # Update last login
            if self.db_manager.db_type == 'postgresql':
                update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = %s"
            else:
                update_query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?"
            
            self.db_manager.execute_update(update_query, (username,))
            
            # Return user info (without sensitive data)
            return {
                'username': user['username'],
                'email': user.get('email'),
                'role': user.get('role', 'Viewer'),
                'permissions': self.ROLES.get(user.get('role', 'Viewer'), {}).get('permissions', []),
                'last_login': user.get('last_login')
            }
        
        return None
    
    def has_permission(self, user: Dict[str, Any], permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user: User dictionary
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        user_permissions = user.get('permissions', [])
        return permission in user_permissions
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users (admin only)."""
        query = "SELECT username, email, role, created_at, last_login FROM users ORDER BY created_at DESC"
        return self.db_manager.execute_query(query)
    
    def update_user_role(self, username: str, new_role: str) -> bool:
        """Update user role (admin only)."""
        if new_role not in self.ROLES:
            raise ValueError(f"Invalid role: {new_role}")
        
        if self.db_manager.db_type == 'postgresql':
            query = "UPDATE users SET role = %s WHERE username = %s"
        else:
            query = "UPDATE users SET role = ? WHERE username = ?"
        
        return self.db_manager.execute_update(query, (new_role, username))
    
    def delete_user(self, username: str) -> bool:
        """Delete a user (admin only)."""
        if self.db_manager.db_type == 'postgresql':
            query = "DELETE FROM users WHERE username = %s"
        else:
            query = "DELETE FROM users WHERE username = ?"
        
        return self.db_manager.execute_update(query, (username,))
    
    def ensure_schema(self):
        """Ensure user table has required columns."""
        # Add password_hash and password_salt columns if they don't exist
        if self.db_manager.db_type == 'postgresql':
            alter_queries = [
                """
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS password_hash TEXT,
                ADD COLUMN IF NOT EXISTS password_salt TEXT
                """,
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"
            ]
        else:
            # SQLite - check if columns exist first
            check_query = "PRAGMA table_info(users)"
            columns = self.db_manager.execute_query(check_query)
            column_names = [col['name'] for col in columns]
            
            alter_queries = []
            if 'password_hash' not in column_names:
                alter_queries.append("ALTER TABLE users ADD COLUMN password_hash TEXT")
            if 'password_salt' not in column_names:
                alter_queries.append("ALTER TABLE users ADD COLUMN password_salt TEXT")
        
        for query in alter_queries:
            try:
                self.db_manager.execute_update(query)
            except Exception as e:
                # Column might already exist
                pass
    
    def ensure_demo_user(self):
        """Create demo user if it doesn't exist."""
        # Check if demo user exists
        if self.db_manager.db_type == 'postgresql':
            query = "SELECT * FROM users WHERE username = %s"
        else:
            query = "SELECT * FROM users WHERE username = ?"
        
        results = self.db_manager.execute_query(query, ('demo@azure.com',))
        
        if not results:
            # Create demo user with known credentials
            try:
                self.create_user(
                    username='demo@azure.com',
                    password='demo123',
                    email='demo@azure.com',
                    role='Admin'
                )
            except Exception:
                # User might already exist or there's a database error
                pass
