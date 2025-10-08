"""
Database Migration Utility
Migrate data between Replit PostgreSQL and Databricks SQL.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from db_manager import DatabaseManager

class DatabaseMigration:
    """Handle database migration between environments."""
    
    def __init__(self, source_db: DatabaseManager, target_db: Optional[DatabaseManager] = None):
        self.source_db = source_db
        self.target_db = target_db
        self.logger = logging.getLogger(__name__)
    
    def export_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Export all data from source database.
        
        Returns:
            Dictionary of {table_name: [row_dicts]}
        """
        export_data = {}
        
        tables = ['incidents', 'resources', 'settings', 'users', 'audit_log']
        
        for table in tables:
            try:
                query = f"SELECT * FROM {table}"
                rows = self.source_db.execute_query(query)
                export_data[table] = rows
                self.logger.info(f"Exported {len(rows)} rows from {table}")
            except Exception as e:
                self.logger.error(f"Failed to export {table}: {e}")
                export_data[table] = []
        
        return export_data
    
    def export_to_json(self, filepath: str) -> bool:
        """
        Export database to JSON file.
        
        Args:
            filepath: Path to save JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = self.export_data()
            
            # Convert datetime objects to strings
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            # Process each table's data
            for table, rows in data.items():
                for row in rows:
                    for key, value in row.items():
                        row[key] = convert_datetime(value)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Database exported to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Export to JSON failed: {e}")
            return False
    
    def import_from_json(self, filepath: str) -> bool:
        """
        Import database from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            True if successful, False otherwise
        """
        if not self.target_db:
            self.logger.error("No target database configured")
            return False
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Import data to target database
            for table, rows in data.items():
                for row in rows:
                    self._import_row(table, row)
            
            self.logger.info(f"Database imported from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Import from JSON failed: {e}")
            return False
    
    def migrate_to_target(self) -> Dict[str, Any]:
        """
        Migrate data from source to target database.
        
        Returns:
            Migration statistics
        """
        if not self.target_db:
            raise Exception("No target database configured")
        
        stats = {
            'start_time': datetime.now().isoformat(),
            'tables': {},
            'total_rows': 0,
            'errors': []
        }
        
        # Export data from source
        data = self.export_data()
        
        # Import to target
        for table, rows in data.items():
            success_count = 0
            error_count = 0
            
            for row in rows:
                try:
                    if self._import_row(table, row):
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    error_count += 1
                    stats['errors'].append(f"{table}: {str(e)}")
            
            stats['tables'][table] = {
                'total': len(rows),
                'success': success_count,
                'errors': error_count
            }
            stats['total_rows'] += success_count
        
        stats['end_time'] = datetime.now().isoformat()
        stats['status'] = 'completed' if not stats['errors'] else 'completed_with_errors'
        
        return stats
    
    def _import_row(self, table: str, row: Dict[str, Any]) -> bool:
        """
        Import a single row to target database.
        
        Args:
            table: Table name
            row: Row data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.target_db:
            return False
        
        try:
            # Remove id field (will be auto-generated)
            row_data = {k: v for k, v in row.items() if k != 'id'}
            
            # Build INSERT query
            columns = list(row_data.keys())
            values = list(row_data.values())
            
            if self.target_db.db_type == 'postgresql':
                placeholders = ', '.join(['%s'] * len(columns))
            else:
                placeholders = ', '.join(['?'] * len(columns))
            
            query = f"""
                INSERT INTO {table} ({', '.join(columns)})
                VALUES ({placeholders})
            """
            
            return self.target_db.execute_update(query, tuple(values))
            
        except Exception as e:
            self.logger.error(f"Failed to import row to {table}: {e}")
            return False
    
    def validate_migration(self) -> Dict[str, Any]:
        """
        Validate migration by comparing row counts.
        
        Returns:
            Validation results
        """
        if not self.target_db:
            raise Exception("No target database configured")
        
        results = {
            'valid': True,
            'tables': {}
        }
        
        tables = ['incidents', 'resources', 'settings', 'users', 'audit_log']
        
        for table in tables:
            try:
                source_count = len(self.source_db.execute_query(f"SELECT COUNT(*) as count FROM {table}"))
                target_count = len(self.target_db.execute_query(f"SELECT COUNT(*) as count FROM {table}"))
                
                match = source_count == target_count
                
                results['tables'][table] = {
                    'source_count': source_count,
                    'target_count': target_count,
                    'match': match
                }
                
                if not match:
                    results['valid'] = False
                    
            except Exception as e:
                results['tables'][table] = {
                    'error': str(e)
                }
                results['valid'] = False
        
        return results
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """
        Create a backup of the current database.
        
        Args:
            backup_name: Optional backup name (timestamp used if not provided)
            
        Returns:
            Backup filepath
        """
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        filepath = f"backups/{backup_name}.json"
        
        import os
        os.makedirs('backups', exist_ok=True)
        
        self.export_to_json(filepath)
        
        return filepath
