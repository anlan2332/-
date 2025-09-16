#!/usr/bin/env python3
"""
Database Migration Script for BaiKaoTong AI Writing Platform
"""

import os
import sys
import logging
from datetime import datetime
import psycopg2
from psycopg2 import sql
import sqlite3

# Add backend path to Python path
sys.path.append('/app/backend/src')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'postgresql')
        self.migrations_path = '/app/scripts/migrations'
        self.migration_table = 'schema_migrations'
        
    def get_connection(self):
        """Get database connection based on DB_TYPE"""
        if self.db_type == 'postgresql':
            return psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'baikao_db'),
                user=os.getenv('DB_USER', 'baikao_user'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT', 5432)
            )
        elif self.db_type == 'sqlite':
            db_path = os.getenv('DB_PATH', '/app/data/local.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            return sqlite3.connect(db_path)
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def create_migration_table(self, cursor):
        """Create migrations tracking table"""
        if self.db_type == 'postgresql':
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.migration_table} (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) UNIQUE NOT NULL,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:  # sqlite
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.migration_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    description TEXT,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def get_applied_migrations(self, cursor):
        """Get list of applied migrations"""
        try:
            cursor.execute(f"SELECT version FROM {self.migration_table} ORDER BY version")
            return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []
    
    def apply_migration(self, cursor, version, description, sql_content):
        """Apply a single migration"""
        try:
            # Execute migration SQL
            cursor.execute(sql_content)
            
            # Record migration
            if self.db_type == 'postgresql':
                cursor.execute(
                    f"INSERT INTO {self.migration_table} (version, description) VALUES (%s, %s)",
                    (version, description)
                )
            else:  # sqlite
                cursor.execute(
                    f"INSERT INTO {self.migration_table} (version, description) VALUES (?, ?)",
                    (version, description)
                )
            
            logger.info(f"Applied migration {version}: {description}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {str(e)}")
            return False
    
    def run_migrations(self):
        """Run all pending migrations"""
        logger.info("Starting database migration...")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create migration table
            self.create_migration_table(cursor)
            conn.commit()
            
            # Get applied migrations
            applied = self.get_applied_migrations(cursor)
            logger.info(f"Found {len(applied)} applied migrations")
            
            # Load and apply pending migrations
            migrations = self.load_migrations()
            pending = [m for m in migrations if m['version'] not in applied]
            
            logger.info(f"Found {len(pending)} pending migrations")
            
            for migration in pending:
                success = self.apply_migration(
                    cursor, 
                    migration['version'], 
                    migration['description'], 
                    migration['sql']
                )
                if not success:
                    conn.rollback()
                    return False
                conn.commit()
            
            cursor.close()
            conn.close()
            
            logger.info("Migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return False
    
    def load_migrations(self):
        """Load migration files from directory"""
        migrations = []
        
        # Built-in migrations
        migrations.extend([
            {
                'version': '001_initial_schema',
                'description': 'Initial database schema',
                'sql': self.get_initial_schema()
            },
            {
                'version': '002_add_indexes',
                'description': 'Add performance indexes',
                'sql': self.get_indexes_sql()
            }
        ])
        
        # Load from files if directory exists
        if os.path.exists(self.migrations_path):
            for filename in sorted(os.listdir(self.migrations_path)):
                if filename.endswith('.sql'):
                    version = filename.replace('.sql', '')
                    filepath = os.path.join(self.migrations_path, filename)
                    with open(filepath, 'r') as f:
                        sql_content = f.read()
                    migrations.append({
                        'version': version,
                        'description': f'Migration from {filename}',
                        'sql': sql_content
                    })
        
        return sorted(migrations, key=lambda x: x['version'])
    
    def get_initial_schema(self):
        """Get initial schema SQL for the database type"""
        if self.db_type == 'postgresql':
            return """
            -- Initial PostgreSQL schema
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS papers (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                content TEXT,
                outline TEXT,
                references TEXT,
                status VARCHAR(20) DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS proposals (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
                filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                content TEXT,
                analysis_result TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                paper_id INTEGER REFERENCES papers(id) ON DELETE SET NULL,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                payment_method VARCHAR(50),
                payment_status VARCHAR(20) DEFAULT 'unpaid',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS reference_sources (
                id SERIAL PRIMARY KEY,
                paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
                title VARCHAR(500) NOT NULL,
                authors TEXT,
                publication VARCHAR(200),
                year INTEGER,
                doi VARCHAR(100),
                url VARCHAR(500),
                abstract TEXT,
                relevance_score DECIMAL(3,2) DEFAULT 0.0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        else:  # sqlite
            return """
            -- Initial SQLite schema
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                content TEXT,
                outline TEXT,
                references TEXT,
                status TEXT DEFAULT 'draft',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                content TEXT,
                analysis_result TEXT,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                paper_id INTEGER REFERENCES papers(id) ON DELETE SET NULL,
                order_number TEXT UNIQUE NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                payment_status TEXT DEFAULT 'unpaid',
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS reference_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id INTEGER REFERENCES papers(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                authors TEXT,
                publication TEXT,
                year INTEGER,
                doi TEXT,
                url TEXT,
                abstract TEXT,
                relevance_score REAL DEFAULT 0.0,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
    
    def get_indexes_sql(self):
        """Get index creation SQL"""
        return """
        -- Performance indexes
        CREATE INDEX IF NOT EXISTS idx_papers_user_id ON papers(user_id);
        CREATE INDEX IF NOT EXISTS idx_papers_status ON papers(status);
        CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
        CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
        CREATE INDEX IF NOT EXISTS idx_references_paper_id ON reference_sources(paper_id);
        """

if __name__ == '__main__':
    migrator = DatabaseMigrator()
    success = migrator.run_migrations()
    sys.exit(0 if success else 1)