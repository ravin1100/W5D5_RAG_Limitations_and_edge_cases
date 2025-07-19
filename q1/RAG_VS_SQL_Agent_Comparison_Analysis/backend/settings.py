"""
Configuration Management for E-commerce SQL Agent

This file centralizes all application settings and configuration values.
It loads environment variables from .env file and provides default values
for development and production environments.

Author: Your Name
Date: July 2025
"""

import os
import logging
from typing import List, Optional
from dotenv import load_dotenv

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

def load_environment_variables():
    """
    Load environment variables from .env file
    
    This function attempts to load the .env file and handles cases where
    the file might not exist (useful for production deployments)
    """
    try:
        # Load .env file from the root directory
        load_dotenv()
        print("=" * 60)
        print("✅ Environment variables loaded successfully from .env file")
        print("=" * 60)
    except FileNotFoundError:
        print("=" * 60)
        print("⚠️  .env file not found - using system environment variables")
        print("=" * 60)
    except Exception as e:
        print("=" * 60)
        print(f"❌ Error loading environment variables: {e}")
        print("=" * 60)

# Load environment variables when this module is imported
load_environment_variables()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# PostgreSQL database connection settings
# These values are loaded from environment variables with sensible defaults
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_NAME = os.getenv('DB_NAME', 'ecommerce_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# Construct database URL for SQLAlchemy and psycopg2
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def validate_database_config():
    """
    Validate that all required database configuration is present
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    required_fields = {
        'DB_HOST': DB_HOST,
        'DB_NAME': DB_NAME,
        'DB_USER': DB_USER,
        'DB_PASSWORD': DB_PASSWORD
    }
    
    missing_fields = []
    for field, value in required_fields.items():
        if not value:
            missing_fields.append(field)
    
    if missing_fields:
        print("=" * 60)
        print("❌ Missing required database configuration:")
        for field in missing_fields:
            print(f"   - {field}")
        print("=" * 60)
        return False
    
    print("=" * 60)
    print("✅ Database configuration validated successfully")
    print(f"   - Host: {DB_HOST}:{DB_PORT}")
    print(f"   - Database: {DB_NAME}")
    print(f"   - User: {DB_USER}")
    print("=" * 60)
    return True

# ============================================================================
# GOOGLE GEMINI API CONFIGURATION
# ============================================================================

# Google AI (Gemini) API settings for LLM operations
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
GEMINI_TEMPERATURE = float(os.getenv('GEMINI_TEMPERATURE', '0.1'))  # Low temperature for consistent SQL generation
GEMINI_MAX_TOKENS = int(os.getenv('GEMINI_MAX_TOKENS', '2048'))

def validate_gemini_config():
    """
    Validate Google Gemini API configuration
    
    Returns:
        bool: True if API key is present, False otherwise
    """
    if not GOOGLE_API_KEY:
        print("=" * 60)
        print("❌ GOOGLE_API_KEY is missing!")
        print("   Please set your Gemini API key in the .env file")
        print("=" * 60)
        return False
    
    print("=" * 60)
    print("✅ Gemini API configuration validated")
    print(f"   - Model: {GEMINI_MODEL}")
    print(f"   - Temperature: {GEMINI_TEMPERATURE}")
    print(f"   - Max Tokens: {GEMINI_MAX_TOKENS}")
    print("=" * 60)
    return True

# ============================================================================
# LANGSMITH CONFIGURATION (for LLM tracing and monitoring)
# ============================================================================

# LangSmith settings for tracing LLM calls and debugging
LANGCHAIN_TRACING_V2 = os.getenv('LANGSMITH_TRACING_V2', 'true').lower() == 'true'
LANGCHAIN_ENDPOINT = os.getenv('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com')
LANGCHAIN_API_KEY = os.getenv('LANGSMITH_API_KEY', '')
LANGCHAIN_PROJECT = os.getenv('LANGSMITH_PROJECT', 'W5D5_Q1_SQL_AGENT')

def setup_langsmith_tracing():
    """
    Configure LangSmith tracing for monitoring LLM operations
    
    This helps track all LLM calls, agent decisions, and chain executions
    for debugging and optimization purposes
    """
    if LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY:
        # Set environment variables for LangSmith
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        os.environ['LANGCHAIN_ENDPOINT'] = LANGCHAIN_ENDPOINT
        os.environ['LANGCHAIN_API_KEY'] = LANGCHAIN_API_KEY
        os.environ['LANGCHAIN_PROJECT'] = LANGCHAIN_PROJECT
        
        print("=" * 60)
        print("✅ LangSmith tracing enabled")
        print(f"   - Project: {LANGCHAIN_PROJECT}")
        print(f"   - Endpoint: {LANGCHAIN_ENDPOINT}")
        print("=" * 60)
    else:
        print("=" * 60)
        print("⚠️  LangSmith tracing disabled (API key missing or tracing=false)")
        print("=" * 60)

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

# General application configuration
APP_DEBUG = os.getenv('APP_DEBUG', 'true').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# SQL Agent specific settings
MAX_SQL_RETRIES = int(os.getenv('MAX_SQL_RETRIES', '3'))  # Number of times to retry SQL generation
QUERY_TIMEOUT = int(os.getenv('QUERY_TIMEOUT', '30'))    # Timeout for SQL queries in seconds
DEFAULT_QUERY_LIMIT = int(os.getenv('DEFAULT_QUERY_LIMIT', '100'))  # Default LIMIT for SELECT queries

# Security settings
ALLOWED_SQL_OPERATIONS: List[str] = os.getenv('ALLOWED_SQL_OPERATIONS', 'SELECT').split(',')
MAX_QUERY_LENGTH = int(os.getenv('MAX_QUERY_LENGTH', '1000'))  # Maximum allowed SQL query length

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================

# FastAPI backend server settings
BACKEND_HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
BACKEND_PORT = int(os.getenv('BACKEND_PORT', '8000'))

# Streamlit frontend settings
FRONTEND_PORT = int(os.getenv('FRONTEND_PORT', '8501'))

# CORS (Cross-Origin Resource Sharing) settings
ALLOWED_ORIGINS: List[str] = os.getenv('ALLOWED_ORIGINS', 'http://localhost:8501,http://127.0.0.1:8501').split(',')

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging():
    """
    Configure application logging with appropriate level and format
    
    This creates a consistent logging format across the entire application
    and sets the appropriate logging level based on configuration
    """
    # Create logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console output
        ]
    )
    
    print("=" * 60)
    print(f"✅ Logging configured with level: {LOG_LEVEL}")
    print("=" * 60)
    
    return logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_all_settings():
    """
    Validate all application settings and configurations
    
    This function checks all critical configuration values and reports
    any missing or invalid settings that could cause runtime errors
    
    Returns:
        bool: True if all settings are valid, False otherwise
    """
    print("=" * 80)
    print("🔧 VALIDATING APPLICATION CONFIGURATION")
    print("=" * 80)
    
    validation_results = []
    
    # Validate database configuration
    validation_results.append(validate_database_config())
    
    # Validate Gemini API configuration
    validation_results.append(validate_gemini_config())
    
    # Setup LangSmith tracing
    setup_langsmith_tracing()
    
    # Setup logging
    setup_logging()
    
    # Print summary
    if all(validation_results):
        print("=" * 80)
        print("✅ ALL CONFIGURATIONS VALIDATED SUCCESSFULLY!")
        print("🚀 Application is ready to start")
        print("=" * 80)
        return True
    else:
        print("=" * 80)
        print("❌ CONFIGURATION VALIDATION FAILED!")
        print("❌ Please fix the missing configuration values")
        print("=" * 80)
        return False

# ============================================================================
# INITIALIZE SETTINGS
# ============================================================================

# Validate all settings when this module is imported
# This ensures that configuration issues are caught early
if __name__ == "__main__":
    # Only validate when running this file directly
    validate_all_settings()
else:
    # When imported, just show a brief status
    print("=" * 50)
    print("📋 Settings module loaded")
    print(f"🌍 Environment: {ENVIRONMENT}")
    print(f"🔧 Debug mode: {APP_DEBUG}")
    print("=" * 50)

# Export commonly used settings for easy importing
__all__ = [
    'DATABASE_URL', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
    'GOOGLE_API_KEY', 'GEMINI_MODEL', 'GEMINI_TEMPERATURE', 'GEMINI_MAX_TOKENS',
    'LANGCHAIN_PROJECT', 'LANGCHAIN_TRACING_V2',
    'APP_DEBUG', 'LOG_LEVEL', 'ENVIRONMENT',
    'MAX_SQL_RETRIES', 'QUERY_TIMEOUT', 'DEFAULT_QUERY_LIMIT',
    'ALLOWED_SQL_OPERATIONS', 'MAX_QUERY_LENGTH',
    'BACKEND_HOST', 'BACKEND_PORT', 'FRONTEND_PORT', 'ALLOWED_ORIGINS',
    'validate_all_settings'
]
