"""
FastAPI Main Application for E-commerce SQL Agent

This is the main FastAPI application that serves as the backend API for the
natural language to SQL agent system. It provides REST endpoints for the
Streamlit frontend and integrates all the backend components.

Author: SQL Agent Project
Date: July 19, 2025
"""

import logging
import time
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

# FastAPI imports
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware

# Import our modules
from models import QueryRequest, QueryResponse, ErrorResponse, SystemStatus
from sql_agent import get_sql_agent, is_agent_ready
from postgres import is_database_ready, get_database_manager
from llm_chain import is_chains_ready
from settings import (
    ALLOWED_ORIGINS, BACKEND_HOST, BACKEND_PORT, APP_DEBUG, 
    validate_all_settings, setup_langsmith_tracing
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global application state
app_state = {
    "start_time": time.time(),
    "total_queries_processed": 0,
    "successful_queries": 0,
    "failed_queries": 0
}

# ============================================================================
# APPLICATION LIFECYCLE MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events
    """
    # ========================================================================
    # STARTUP
    # ========================================================================
    print("=" * 100)
    print("🚀 STARTING E-COMMERCE SQL AGENT API SERVER")
    print("=" * 100)
    
    try:
        # Validate all configuration settings
        print("🔧 Step 1: Validating configuration...")
        if not validate_all_settings():
            raise Exception("Configuration validation failed")
        print("✅ Configuration validated successfully")
        
        # Setup LangSmith tracing
        print("📊 Step 2: Setting up LangSmith tracing...")
        setup_langsmith_tracing()
        print("✅ LangSmith tracing configured")
        
        # Check database readiness
        print("🗃️  Step 3: Checking database connection...")
        if not is_database_ready():
            raise Exception("Database not ready")
        print("✅ Database connection verified")
        
        # Check LLM chains readiness
        print("🤖 Step 4: Checking LLM chains...")
        if not is_chains_ready():
            raise Exception("LLM chains not ready")
        print("✅ LLM chains initialized")
        
        # Check SQL agent readiness
        print("🎯 Step 5: Checking SQL agent...")
        if not is_agent_ready():
            raise Exception("SQL agent not ready")
        print("✅ SQL agent ready")
        
        print("=" * 100)
        print("🎉 API SERVER STARTUP COMPLETED SUCCESSFULLY!")
        print(f"   Server: http://{BACKEND_HOST}:{BACKEND_PORT}")
        print(f"   Debug mode: {APP_DEBUG}")
        print(f"   Documentation: http://{BACKEND_HOST}:{BACKEND_PORT}/docs")
        print("=" * 100)
        
        # Record startup time
        app_state["start_time"] = time.time()
        
        yield  # Application is running
        
    except Exception as e:
        print("=" * 100)
        print("❌ API SERVER STARTUP FAILED!")
        print(f"   Error: {e}")
        print("=" * 100)
        raise
    
    # ========================================================================
    # SHUTDOWN
    # ========================================================================
    print("=" * 100)
    print("🛑 SHUTTING DOWN API SERVER")
    print(f"   Uptime: {time.time() - app_state['start_time']:.1f} seconds")
    print(f"   Total queries processed: {app_state['total_queries_processed']}")
    print(f"   Success rate: {app_state['successful_queries']}/{app_state['total_queries_processed']}")
    print("=" * 100)

# ============================================================================
# FASTAPI APPLICATION SETUP
# ============================================================================

# Create FastAPI application with lifecycle management
app = FastAPI(
    title="E-commerce SQL Agent API",
    description="Natural Language to SQL conversion API for customer support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add GZip middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ============================================================================
# DEPENDENCY FUNCTIONS
# ============================================================================

async def get_sql_agent_dependency():
    """
    Dependency to get SQL agent with proper error handling
    """
    agent = get_sql_agent()
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="SQL Agent service is not available"
        )
    return agent

async def log_request_info(request: Request):
    """
    Log incoming request information for monitoring
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    logger.info(f"Request from {client_ip}: {request.method} {request.url}")
    
    return {
        "client_ip": client_ip,
        "user_agent": user_agent,
        "timestamp": time.time()
    }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint providing basic API information
    """
    return {
        "message": "E-commerce SQL Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", response_model=SystemStatus)
async def health_check():
    """
    Health check endpoint for monitoring system status
    """
    print("=" * 60)
    print("🏥 HEALTH CHECK REQUEST")
    print("=" * 60)
    
    try:
        # Check all system components
        database_connected = is_database_ready()
        llm_available = is_chains_ready()
        agent_ready = is_agent_ready()
        
        uptime = time.time() - app_state["start_time"]
        
        status = SystemStatus(
            database_connected=database_connected,
            llm_available=llm_available,
            total_queries_processed=app_state["total_queries_processed"],
            uptime_seconds=uptime
        )
        
        # Log status
        print(f"   Database: {'✅' if database_connected else '❌'}")
        print(f"   LLM: {'✅' if llm_available else '❌'}")
        print(f"   Agent: {'✅' if agent_ready else '❌'}")
        print(f"   Uptime: {uptime:.1f}s")
        print(f"   Total queries: {app_state['total_queries_processed']}")
        print("=" * 60)
        
        return status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")

@app.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    sql_agent = Depends(get_sql_agent_dependency),
    request_info = Depends(log_request_info)
):
    """
    Main endpoint for processing natural language queries
    
    This endpoint handles the complete workflow:
    1. Receives natural language question
    2. Processes through SQL agent
    3. Returns formatted response
    """
    start_time = time.time()
    
    print("=" * 100)
    print("🔥 NEW QUERY REQUEST RECEIVED")
    print(f"   Question: {request.question}")
    print(f"   User ID: {request.user_id or 'Anonymous'}")
    print(f"   Client IP: {request_info['client_ip']}")
    print("=" * 100)
    
    try:
        # Update query counter
        app_state["total_queries_processed"] += 1
        
        # Process the query through SQL agent
        response = sql_agent.process_query(
            question=request.question,
            user_id=request.user_id
        )
        
        # Update success/failure counters
        if response.success:
            app_state["successful_queries"] += 1
        else:
            app_state["failed_queries"] += 1
        
        # Log final response
        processing_time = time.time() - start_time
        
        print("=" * 100)
        print("📊 QUERY PROCESSING COMPLETED")
        print(f"   Success: {response.success}")
        print(f"   Processing time: {processing_time:.3f}s")
        print(f"   Agent execution time: {response.execution_time or 0:.3f}s")
        if response.success:
            print(f"   Rows returned: {response.row_count}")
            print(f"   Answer length: {len(response.answer)} chars")
        else:
            print(f"   Error: {response.error_message}")
        print("=" * 100)
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        app_state["failed_queries"] += 1
        error_msg = f"Unexpected error processing query: {str(e)}"
        logger.error(error_msg)
        
        print("=" * 100)
        print("💥 UNEXPECTED ERROR IN QUERY PROCESSING")
        print(f"   Error: {error_msg}")
        print("=" * 100)
        
        return QueryResponse(
            success=False,
            answer="I encountered an unexpected error while processing your question. Please try again later.",
            sql_query=None,
            row_count=None,
            execution_time=time.time() - start_time,
            error_message=error_msg
        )

@app.get("/stats", response_model=Dict[str, Any])
async def get_statistics():
    """
    Get API usage statistics
    """
    uptime = time.time() - app_state["start_time"]
    success_rate = (
        app_state["successful_queries"] / app_state["total_queries_processed"]
        if app_state["total_queries_processed"] > 0 else 0
    )
    
    return {
        "uptime_seconds": uptime,
        "uptime_formatted": f"{uptime/3600:.1f} hours",
        "total_queries_processed": app_state["total_queries_processed"],
        "successful_queries": app_state["successful_queries"],
        "failed_queries": app_state["failed_queries"],
        "success_rate": f"{success_rate:.2%}",
        "queries_per_minute": app_state["total_queries_processed"] / max(uptime/60, 1),
        "system_status": {
            "database_ready": is_database_ready(),
            "llm_chains_ready": is_chains_ready(),
            "agent_ready": is_agent_ready()
        }
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions with proper logging
    """
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            error_type="HTTP_ERROR",
            error_message=exc.detail,
            details=f"Status code: {exc.status_code}"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions
    """
    error_msg = f"Unexpected server error: {str(exc)}"
    logger.error(f"Unhandled exception: {error_msg} - {request.url}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            error_type="SERVER_ERROR",
            error_message="An unexpected server error occurred",
            details=error_msg if APP_DEBUG else "Contact support for assistance"
        ).dict()
    )

# ============================================================================
# DEVELOPMENT ENDPOINTS (DEBUG MODE ONLY)
# ============================================================================

if APP_DEBUG:
    @app.get("/debug/test-db")
    async def test_database_connection():
        """Test database connection (debug only)"""
        try:
            db_manager = get_database_manager()
            if db_manager and db_manager.test_connection():
                return {"status": "success", "message": "Database connection working"}
            else:
                return {"status": "failed", "message": "Database connection failed"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @app.get("/debug/test-llm")
    async def test_llm_chains():
        """Test LLM chains (debug only)"""
        try:
            chains_ready = is_chains_ready()
            return {
                "status": "success" if chains_ready else "failed",
                "message": f"LLM chains {'ready' if chains_ready else 'not ready'}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Run the FastAPI application directly (for development)
    """
    import uvicorn
    
    print("=" * 80)
    print("🚀 STARTING FASTAPI APPLICATION IN DEVELOPMENT MODE")
    print("=" * 80)
    
    uvicorn.run(
        "main:app",
        host=BACKEND_HOST,
        port=BACKEND_PORT,
        reload=APP_DEBUG,
        log_level="info"
    )
