import os
import json
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

class DatabaseManager:
    """
    Unified database manager that works across different environments.
    Supports PostgreSQL (Replit/Azure) and SQLite (fallback).
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.db_type = None
        self.logger = logging.getLogger(__name__)
        
    def initialize(self) -> bool:
        """
        Initialize database connection and create schema if needed.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to connect to PostgreSQL first (Replit/Azure)
            if self._connect_postgresql():
                self.db_type = 'postgresql'
                self._create_postgresql_schema()
                return True
            
            # Fallback to SQLite
            if self._connect_sqlite():
                self.db_type = 'sqlite'
                self._create_sqlite_schema()
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    def _connect_postgresql(self) -> bool:
        """Connect to PostgreSQL database."""
        try:
            db_config = self.config.get('database', {})
            
            # Try DATABASE_URL first (Replit style)
            if db_config.get('url'):
                self.connection = psycopg2.connect(
                    db_config['url'],
                    cursor_factory=RealDictCursor
                )
            else:
                # Build connection from components
                self.connection = psycopg2.connect(
                    host=db_config.get('host', 'localhost'),
                    port=db_config.get('port', 5432),
                    database=db_config.get('database', 'azure_support'),
                    user=db_config.get('username', 'postgres'),
                    password=db_config.get('password', ''),
                    cursor_factory=RealDictCursor
                )
            
            # Test connection
            cursor = self.connection.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
            cursor.close()
            
            self.logger.info("Connected to PostgreSQL database")
            return True
            
        except Exception as e:
            self.logger.error(f"PostgreSQL connection failed: {e}")
            if self.connection:
                self.connection.close()
                self.connection = None
            return False
    
    def _connect_sqlite(self) -> bool:
        """Connect to SQLite database (fallback)."""
        try:
            # Create data directory if it doesn't exist
            os.makedirs('data', exist_ok=True)
            
            self.connection = sqlite3.connect('data/azure_support.db')
            self.connection.row_factory = sqlite3.Row
            
            # Test connection
            cursor = self.connection.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
            cursor.close()
            
            self.logger.info("Connected to SQLite database")
            return True
            
        except Exception as e:
            self.logger.error(f"SQLite connection failed: {e}")
            if self.connection:
                self.connection.close()
                self.connection = None
            return False
    
    def _create_postgresql_schema(self):
        """Create PostgreSQL database schema."""
        schema_sql = """
        -- Incidents table
        CREATE TABLE IF NOT EXISTS incidents (
            id SERIAL PRIMARY KEY,
            incident_id VARCHAR(50) UNIQUE NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'Open',
            priority VARCHAR(10) DEFAULT 'Medium',
            assignee VARCHAR(100),
            service VARCHAR(50),
            region VARCHAR(50),
            category VARCHAR(50),
            impact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Resources cache table
        CREATE TABLE IF NOT EXISTS resources (
            id SERIAL PRIMARY KEY,
            resource_id VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            type VARCHAR(100),
            resource_group VARCHAR(100),
            subscription_id VARCHAR(100),
            region VARCHAR(50),
            status VARCHAR(50),
            tags JSONB,
            properties JSONB,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Settings table
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            key VARCHAR(100) UNIQUE NOT NULL,
            value JSONB,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Users/preferences table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255),
            role VARCHAR(50) DEFAULT 'Viewer',
            preferences JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        
        -- Audit log table
        CREATE TABLE IF NOT EXISTS audit_log (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100),
            action VARCHAR(100) NOT NULL,
            resource_type VARCHAR(50),
            resource_id VARCHAR(255),
            details JSONB,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
        CREATE INDEX IF NOT EXISTS idx_incidents_assignee ON incidents(assignee);
        CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(type);
        CREATE INDEX IF NOT EXISTS idx_resources_rg ON resources(resource_group);
        CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
        """
        
        cursor = self.connection.cursor()
        cursor.execute(schema_sql)
        self.connection.commit()
        cursor.close()
        
        self.logger.info("PostgreSQL schema created successfully")
    
    def _create_sqlite_schema(self):
        """Create SQLite database schema."""
        schema_sql = """
        -- Incidents table
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Open',
            priority TEXT DEFAULT 'Medium',
            assignee TEXT,
            service TEXT,
            region TEXT,
            category TEXT,
            impact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Resources cache table
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            type TEXT,
            resource_group TEXT,
            subscription_id TEXT,
            region TEXT,
            status TEXT,
            tags TEXT, -- JSON as TEXT
            properties TEXT, -- JSON as TEXT
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Settings table
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT, -- JSON as TEXT
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Users/preferences table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'Viewer',
            preferences TEXT, -- JSON as TEXT
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        
        -- Audit log table
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id TEXT,
            details TEXT, -- JSON as TEXT
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);
        CREATE INDEX IF NOT EXISTS idx_incidents_assignee ON incidents(assignee);
        CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(type);
        CREATE INDEX IF NOT EXISTS idx_resources_rg ON resources(resource_group);
        CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
        """
        
        cursor = self.connection.cursor()
        cursor.executescript(schema_sql)
        self.connection.commit()
        cursor.close()
        
        self.logger.info("SQLite schema created successfully")
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of row dictionaries
        """
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            
            # Convert to list of dictionaries
            if self.db_type == 'postgresql':
                return [dict(row) for row in results]
            else:  # SQLite
                return [dict(row) for row in results]
                
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return []
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> bool:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Update execution failed: {e}")
            self.connection.rollback()
            return False
    
    def get_incidents(self, status: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Get incidents from database."""
        query = "SELECT * FROM incidents"
        params = None
        
        if status:
            query += " WHERE status = %s" if self.db_type == 'postgresql' else " WHERE status = ?"
            params = (status,)
        
        query += " ORDER BY created_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query, params)
    
    def create_incident(self, incident_data: Dict[str, Any]) -> bool:
        """Create a new incident."""
        if self.db_type == 'postgresql':
            query = """
                INSERT INTO incidents (incident_id, title, description, status, priority, 
                                     assignee, service, region, category, impact)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        else:
            query = """
                INSERT INTO incidents (incident_id, title, description, status, priority,
                                     assignee, service, region, category, impact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
        
        params = (
            incident_data.get('incident_id'),
            incident_data.get('title'),
            incident_data.get('description'),
            incident_data.get('status', 'Open'),
            incident_data.get('priority', 'Medium'),
            incident_data.get('assignee'),
            incident_data.get('service'),
            incident_data.get('region'),
            incident_data.get('category'),
            incident_data.get('impact')
        )
        
        return self.execute_update(query, params)
    
    def update_incident(self, incident_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing incident."""
        set_clauses = []
        params = []
        
        for key, value in update_data.items():
            if key != 'incident_id':  # Don't update the ID
                set_clauses.append(f"{key} = %s" if self.db_type == 'postgresql' else f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return False
        
        # Add updated_at
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(incident_id)
        
        query = f"""
            UPDATE incidents 
            SET {', '.join(set_clauses)}
            WHERE incident_id = %s
        """ if self.db_type == 'postgresql' else f"""
            UPDATE incidents 
            SET {', '.join(set_clauses)}
            WHERE incident_id = ?
        """
        
        return self.execute_update(query, tuple(params))
    
    def get_setting(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a setting value."""
        query = "SELECT value FROM settings WHERE key = %s" if self.db_type == 'postgresql' else "SELECT value FROM settings WHERE key = ?"
        results = self.execute_query(query, (key,))
        
        if results:
            value = results[0]['value']
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
        
        return None
    
    def set_setting(self, key: str, value: Any, description: Optional[str] = None) -> bool:
        """Set a setting value."""
        # Convert value to JSON string for SQLite
        json_value = json.dumps(value) if self.db_type == 'sqlite' else value
        
        if self.db_type == 'postgresql':
            query = """
                INSERT INTO settings (key, value, description) 
                VALUES (%s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET 
                    value = EXCLUDED.value,
                    description = EXCLUDED.description,
                    updated_at = CURRENT_TIMESTAMP
            """
        else:
            query = """
                INSERT OR REPLACE INTO settings (key, value, description, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """
        
        return self.execute_update(query, (key, json_value, description))
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info("Database connection closed")
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        try:
            if not self.connection:
                return False
            
            cursor = self.connection.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
            cursor.close()
            return True
            
        except Exception:
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get database health status."""
        status = {
            'connected': self.is_connected(),
            'type': self.db_type,
            'tables': []
        }
        
        if status['connected']:
            try:
                # Get table information
                if self.db_type == 'postgresql':
                    query = """
                        SELECT table_name, 
                               (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
                        FROM information_schema.tables t
                        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    """
                else:
                    query = """
                        SELECT name as table_name,
                               (SELECT COUNT(*) FROM pragma_table_info(name)) as column_count
                        FROM sqlite_master 
                        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                    """
                
                results = self.execute_query(query)
                status['tables'] = results
                
            except Exception as e:
                status['error'] = str(e)
        
        return status
