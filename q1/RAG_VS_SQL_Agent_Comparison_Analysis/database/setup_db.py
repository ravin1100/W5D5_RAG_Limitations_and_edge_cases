"""
Database Setup Script for E-commerce SQL Agent

This script sets up the complete database schema and populates it with sample data.
It handles connection management, error handling, and provides detailed feedback
during the setup process.

Author: SQL Agent Project
Date: July 19, 2025
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from pathlib import Path

# Add the backend directory to Python path so we can import settings
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from settings import (
        DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, 
        validate_database_config
    )
    print("=" * 80)
    print("✅ Successfully imported database configuration from settings.py")
    print("=" * 80)
except ImportError as e:
    print("=" * 80)
    print("❌ Error importing database settings!")
    print(f"   Make sure backend/settings.py exists and .env is configured")
    print(f"   Error: {e}")
    print("=" * 80)
    sys.exit(1)

def check_database_connection():
    """
    Test database connection before attempting setup
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    print("🔍 Testing database connection...")
    
    try:
        # Attempt to connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=10  # 10 second timeout
        )
        
        # Test the connection with a simple query
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        print("=" * 80)
        print("✅ DATABASE CONNECTION SUCCESSFUL!")
        print(f"   Connected to: {DB_NAME}@{DB_HOST}:{DB_PORT}")
        print(f"   PostgreSQL Version: {version}")
        print("=" * 80)
        return True
        
    except psycopg2.OperationalError as e:
        print("=" * 80)
        print("❌ DATABASE CONNECTION FAILED!")
        print(f"   Host: {DB_HOST}:{DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        print(f"   Error: {e}")
        print("=" * 80)
        print("💡 Troubleshooting tips:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check your .env file has correct database credentials")
        print("   3. Verify the database exists and user has proper permissions")
        print("=" * 80)
        return False
        
    except Exception as e:
        print("=" * 80)
        print(f"❌ Unexpected error during connection test: {e}")
        print("=" * 80)
        return False

def execute_sql_file(file_path, description):
    """
    Execute SQL commands from a file
    
    Args:
        file_path (str): Path to the SQL file
        description (str): Description of what the file does
        
    Returns:
        bool: True if execution successful, False otherwise
    """
    print("=" * 80)
    print(f"📁 Executing {description}")
    print(f"   File: {file_path}")
    print("=" * 80)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ SQL file not found: {file_path}")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        # Enable autocommit to handle transactions properly
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Read and execute the SQL file
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
            
        print(f"📖 Reading SQL file... ({len(sql_content)} characters)")
        
        # Execute the SQL content
        cur.execute(sql_content)
        
        print(f"✅ {description} completed successfully!")
        
        # Close connections
        cur.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error during {description}:")
        print(f"   Error Code: {e.pgcode}")
        print(f"   Error Message: {e.pgerror}")
        return False
        
    except FileNotFoundError:
        print(f"❌ SQL file not found: {file_path}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error during {description}: {e}")
        return False

def verify_setup():
    """
    Verify that the database setup was successful by checking table existence
    and row counts
    
    Returns:
        bool: True if verification successful, False otherwise
    """
    print("=" * 80)
    print("🔍 VERIFYING DATABASE SETUP")
    print("=" * 80)
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        
        # Expected tables
        expected_tables = ['customers', 'products', 'orders', 'reviews', 'support_tickets']
        
        # Check if all tables exist and get row counts
        table_info = {}
        for table in expected_tables:
            try:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, (table,))
                
                table_exists = cur.fetchone()[0]
                
                if table_exists:
                    # Get row count
                    cur.execute(f"SELECT COUNT(*) FROM {table};")
                    row_count = cur.fetchone()[0]
                    table_info[table] = row_count
                    print(f"   ✅ {table}: {row_count} records")
                else:
                    print(f"   ❌ {table}: Table does not exist!")
                    cur.close()
                    conn.close()
                    return False
                    
            except Exception as e:
                print(f"   ❌ {table}: Error checking table - {e}")
                cur.close()
                conn.close()
                return False
        
        # Check total records
        total_records = sum(table_info.values())
        
        cur.close()
        conn.close()
        
        print("=" * 80)
        print("🎉 DATABASE SETUP VERIFICATION SUCCESSFUL!")
        print(f"   Total records across all tables: {total_records}")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def main():
    """
    Main function to orchestrate the complete database setup process
    """
    print("=" * 100)
    print("🚀 E-COMMERCE DATABASE SETUP STARTING")
    print("   This script will create tables and insert sample data")
    print("=" * 100)
    
    # Step 1: Validate configuration
    if not validate_database_config():
        print("❌ Database configuration validation failed!")
        sys.exit(1)
    
    # Step 2: Test database connection
    if not check_database_connection():
        print("❌ Cannot proceed without database connection!")
        sys.exit(1)
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Define file paths
    schema_file = script_dir / 'schema.sql'
    sample_data_file = script_dir / 'sample_data.sql'
    
    # Step 3: Execute schema creation
    if not execute_sql_file(schema_file, "Database Schema Creation"):
        print("❌ Schema creation failed! Cannot proceed.")
        sys.exit(1)
    
    # Step 4: Insert sample data
    if not execute_sql_file(sample_data_file, "Sample Data Insertion"):
        print("❌ Sample data insertion failed!")
        print("⚠️  Tables were created but no sample data was inserted.")
        sys.exit(1)
    
    # Step 5: Verify setup
    if not verify_setup():
        print("❌ Database verification failed!")
        sys.exit(1)
    
    # Success!
    print("=" * 100)
    print("🎉 DATABASE SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 100)
    print("✅ All tables created with proper relationships")
    print("✅ Sample data inserted for testing")
    print("✅ Database verification passed")
    print("=" * 100)
    print("🚀 Your SQL Agent system is ready to use!")
    print("=" * 100)
    print("💡 Next steps:")
    print("   1. Test some queries manually in your PostgreSQL client")
    print("   2. Proceed with building the backend API (backend/models.py)")
    print("   3. Set up your Gemini API key in the .env file")
    print("=" * 100)

if __name__ == "__main__":
    """
    Run the database setup when script is executed directly
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("⚠️  Setup interrupted by user")
        print("=" * 80)
        sys.exit(1)
    except Exception as e:
        print("=" * 80)
        print(f"💥 Unexpected error during setup: {e}")
        print("=" * 80)
        sys.exit(1)
