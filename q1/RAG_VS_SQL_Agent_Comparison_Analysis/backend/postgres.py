"""
PostgreSQL Database Integration for E-commerce SQL Agent

This module handles all database operations using LangChain's SQL toolkit.
It provides database connection management, schema introspection, and
SQL execution capabilities for the natural language SQL agent.

Author: SQL Agent Project
Date: July 19, 2025
"""

import logging
import time
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager

import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# LangChain imports for SQL toolkit
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLDatabaseTool
)

# Import our settings
from settings import (
    DATABASE_URL, DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    QUERY_TIMEOUT, DEFAULT_QUERY_LIMIT
)

# Set up logging
logger = logging.getLogger(__name__)

# ============================================================================
# DATABASE CONNECTION MANAGEMENT
# ============================================================================

class DatabaseManager:
    """
    Manages database connections and provides LangChain SQL toolkit integration
    
    This class handles:
    - Database connection pooling
    - Schema introspection
    - Query execution with timeout and limits
    - Error handling and logging
    """
    
    def __init__(self):
        """Initialize the database manager with connection settings"""
        self.engine: Optional[Engine] = None
        self.sql_db: Optional[SQLDatabase] = None
        self.connection_string = DATABASE_URL
        
        print("=" * 60)
        print("🗃️  Initializing Database Manager")
        print(f"   Database: {DB_NAME}")
        print(f"   Host: {DB_HOST}:{DB_PORT}")
        print("=" * 60)
        
        # Initialize database connection
        self._connect()
    
    def _connect(self) -> bool:
        """
        Establish database connection and initialize LangChain SQL toolkit
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print("🔌 Establishing database connection...")
            
            # Create SQLAlchemy engine
            self.engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=False           # Set to True for SQL query debugging
            )
            
            # Test the connection
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"✅ Connected to PostgreSQL: {version}")
            
            # Initialize LangChain SQL Database
            self.sql_db = SQLDatabase(
                engine=self.engine,
                include_tables=None,  # Include all tables
                sample_rows_in_table_info=3  # Include 3 sample rows in schema info
            )
            
            print("✅ LangChain SQL Database initialized")
            print("=" * 60)
            return True
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            print(f"❌ Database connection failed: {e}")
            print("=" * 60)
            return False
    
    def get_sql_database(self) -> Optional[SQLDatabase]:
        """
        Get the LangChain SQL Database instance
        
        Returns:
            SQLDatabase: The initialized SQL database instance
        """
        if not self.sql_db:
            print("⚠️  SQL Database not initialized, attempting to reconnect...")
            self._connect()
        
        return self.sql_db
    
    def test_connection(self) -> bool:
        """
        Test if database connection is working
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        try:
            if not self.engine:
                return False
            
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1;"))
                return True
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# ============================================================================
# DATABASE TOOLS AND UTILITIES
# ============================================================================

class DatabaseTools:
    """
    Provides LangChain SQL tools for the agent to use
    
    This class wraps LangChain's SQL database tools and provides
    additional utilities for schema introspection and query execution.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize database tools with a database manager"""
        self.db_manager = db_manager
        self.sql_db = db_manager.get_sql_database()
        
        if not self.sql_db:
            raise Exception("Failed to initialize SQL Database")
        
        # Initialize LangChain SQL tools
        self._init_langchain_tools()
    
    def _init_langchain_tools(self):
        """Initialize LangChain SQL database tools"""
        print("🔧 Initializing LangChain SQL Tools...")
        
        try:
            # Tool to get database schema information
            self.info_tool = InfoSQLDatabaseTool(db=self.sql_db)
            
            # Tool to list all tables in the database
            self.list_tool = ListSQLDatabaseTool(db=self.sql_db)
            
            # Tool to execute SQL queries
            self.query_tool = QuerySQLDatabaseTool(db=self.sql_db)
            
            print("✅ LangChain SQL Tools initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain tools: {e}")
            raise
    
    def get_table_list(self) -> List[str]:
        """
        Get list of all tables in the database
        
        Returns:
            List[str]: List of table names
        """
        try:
            result = self.list_tool.run("")
            tables = [table.strip() for table in result.split(',') if table.strip()]
            
            print("=" * 50)
            print("📋 Available Tables:")
            for table in tables:
                print(f"   • {table}")
            print("=" * 50)
            
            return tables
            
        except Exception as e:
            logger.error(f"Failed to get table list: {e}")
            return []
    
    def get_schema_info(self, table_names: Optional[List[str]] = None) -> str:
        """
        Get detailed schema information for specified tables or all tables
        
        Args:
            table_names: List of table names to get info for (None = all tables)
            
        Returns:
            str: Formatted schema information
        """
        try:
            if table_names:
                # Get info for specific tables
                table_list = ', '.join(table_names)
            else:
                # Get info for all tables
                table_list = ''
            
            schema_info = self.info_tool.run(table_list)
            
            print("=" * 60)
            print("📊 Database Schema Information Retrieved")
            print(f"   Tables: {table_names or 'All'}")
            print(f"   Schema size: {len(schema_info)} characters")
            print("=" * 60)
            
            return schema_info
            
        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            return f"Error retrieving schema info: {e}"
    
    def execute_query(self, query: str) -> Tuple[bool, str, Optional[int]]:
        """
        Execute a SQL query safely with proper error handling
        
        Args:
            query: SQL query to execute
            
        Returns:
            Tuple[bool, str, Optional[int]]: (success, result/error, row_count)
        """
        start_time = time.time()
        
        try:
            print("=" * 60)
            print("🔍 Executing SQL Query:")
            print(f"   Query: {query[:100]}{'...' if len(query) > 100 else ''}")
            print("=" * 60)
            
            # Execute query using LangChain tool
            result = self.query_tool.run(query)
            
            execution_time = time.time() - start_time
            
            # Try to determine row count from result
            row_count = None
            if result and isinstance(result, str):
                lines = result.strip().split('\n')
                # Simple heuristic: count non-header lines
                if len(lines) > 1:
                    row_count = len(lines) - 1  # Subtract header line
            
            print("✅ Query executed successfully")
            print(f"   Execution time: {execution_time:.3f} seconds")
            print(f"   Result size: {len(result) if result else 0} characters")
            print(f"   Estimated rows: {row_count}")
            print("=" * 60)
            
            return True, result, row_count
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"Query execution failed: {error_msg}")
            print(f"❌ Query execution failed:")
            print(f"   Error: {error_msg}")
            print(f"   Execution time: {execution_time:.3f} seconds")
            print("=" * 60)
            
            return False, error_msg, None

# ============================================================================
# GLOBAL DATABASE INSTANCE
# ============================================================================

# Initialize global database manager and tools
print("=" * 80)
print("🚀 INITIALIZING POSTGRESQL DATABASE INTEGRATION")
print("=" * 80)

try:
    # Create database manager instance
    db_manager = DatabaseManager()
    
    # Create database tools instance
    db_tools = DatabaseTools(db_manager)
    
    print("=" * 80)
    print("✅ POSTGRESQL INTEGRATION READY!")
    print("   • Database connection established")
    print("   • LangChain SQL Database initialized")
    print("   • SQL tools ready for use")
    print("=" * 80)
    
except Exception as e:
    print("=" * 80)
    print("❌ POSTGRESQL INTEGRATION FAILED!")
    print(f"   Error: {e}")
    print("=" * 80)
    db_manager = None
    db_tools = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_database_tools() -> Optional[DatabaseTools]:
    """
    Get the global database tools instance
    
    Returns:
        DatabaseTools: The initialized database tools instance
    """
    return db_tools

def get_database_manager() -> Optional[DatabaseManager]:
    """
    Get the global database manager instance
    
    Returns:
        DatabaseManager: The initialized database manager instance
    """
    return db_manager

def is_database_ready() -> bool:
    """
    Check if database is ready for operations
    
    Returns:
        bool: True if database is ready, False otherwise
    """
    return db_manager is not None and db_manager.test_connection()

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    'DatabaseManager',
    'DatabaseTools',
    'get_database_tools',
    'get_database_manager',
    'is_database_ready'
]

# ============================================================================
# INITIALIZATION VERIFICATION
# ============================================================================

if __name__ == "__main__":
    """
    Test database integration when run directly
    """
    print("=" * 80)
    print("🧪 TESTING DATABASE INTEGRATION")
    print("=" * 80)
    
    if is_database_ready():
        print("✅ Database is ready!")
        
        # Test getting table list
        if db_tools:
            tables = db_tools.get_table_list()
            print(f"✅ Found {len(tables)} tables")
            
            # Test schema info
            schema = db_tools.get_schema_info()
            print(f"✅ Schema info retrieved ({len(schema)} chars)")
        
        print("=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
    else:
        print("❌ Database not ready!")
        print("=" * 80)
