"""
Frontend Utilities for E-commerce SQL Agent Streamlit Interface

This module provides utility functions for the Streamlit frontend including
API communication, response formatting, UI helpers, and interactive components.
Creates a modern, user-friendly experience for customer support agents.

Author: SQL Agent Project
Date: July 19, 2025
"""

import streamlit as st
import requests
import json
import time
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    "query": f"{API_BASE_URL}/query",
    "health": f"{API_BASE_URL}/health",
    "stats": f"{API_BASE_URL}/stats"
}

# UI Configuration
QUERY_EXAMPLES = [
    "Show all customers with their email addresses",
    "Find all pending orders from the last 7 days",
    "List products with low stock (less than 10 items)",
    "Show all open support tickets with high priority",
    "Find customers who have never placed an order",
    "List all reviews with 5-star ratings",
    "Show order details for customer John Doe",
    "Find products in Electronics category under $100",
    "List all cancelled orders this month",
    "Show customers with unresolved support tickets"
]

# Color scheme for modern UI
COLORS = {
    "primary": "#1f77b4",
    "success": "#2ca02c", 
    "warning": "#ff7f0e",
    "error": "#d62728",
    "info": "#17becf",
    "secondary": "#7f7f7f"
}

# ============================================================================
# API COMMUNICATION FUNCTIONS
# ============================================================================

def check_backend_health() -> Tuple[bool, Dict[str, Any]]:
    """
    Check if the backend API is running and healthy
    
    Returns:
        Tuple[bool, Dict]: (is_healthy, health_data)
    """
    try:
        print("=" * 60)
        print("🏥 Checking backend health...")
        print("=" * 60)
        
        response = requests.get(
            API_ENDPOINTS["health"], 
            timeout=5
        )
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend is healthy!")
            print(f"   Database: {'✅' if health_data.get('database_connected') else '❌'}")
            print(f"   LLM: {'✅' if health_data.get('llm_available') else '❌'}")
            print("=" * 60)
            return True, health_data
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            print("=" * 60)
            return False, {}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("=" * 60)
        return False, {"error": str(e)}

def send_query_to_backend(question: str, user_id: str = "streamlit_user") -> Dict[str, Any]:
    """
    Send a natural language query to the backend API
    
    Args:
        question: Natural language question
        user_id: User identifier
        
    Returns:
        Dict: API response data
    """
    try:
        print("=" * 80)
        print("📤 Sending query to backend...")
        print(f"   Question: {question}")
        print(f"   User ID: {user_id}")
        print("=" * 80)
        
        # Prepare request data
        request_data = {
            "question": question,
            "user_id": user_id
        }
        
        # Send request with timeout
        response = requests.post(
            API_ENDPOINTS["query"],
            json=request_data,
            timeout=60,  # 60 second timeout for complex queries
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Response received: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query processed successfully!")
            print("=" * 80)
            return result
        else:
            error_msg = f"API Error: {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", error_msg)
            except:
                pass
            
            print(f"❌ {error_msg}")
            print("=" * 80)
            return {
                "success": False,
                "error_message": error_msg,
                "answer": f"Backend error: {error_msg}"
            }
            
    except requests.exceptions.Timeout:
        error_msg = "Query timed out. Please try a simpler question."
        print(f"⏱️ {error_msg}")
        print("=" * 80)
        return {
            "success": False,
            "error_message": "Timeout",
            "answer": error_msg
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Cannot connect to backend: {str(e)}"
        print(f"🔌 {error_msg}")
        print("=" * 80)
        return {
            "success": False,
            "error_message": "Connection Error",
            "answer": error_msg
        }

def get_api_statistics() -> Optional[Dict[str, Any]]:
    """
    Get API usage statistics from the backend
    
    Returns:
        Dict: Statistics data or None if unavailable
    """
    try:
        response = requests.get(API_ENDPOINTS["stats"], timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================

def setup_page_config():
    """
    Configure Streamlit page settings for modern appearance
    """
    st.set_page_config(
        page_title="E-commerce SQL Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo',
            'Report a bug': "https://github.com/your-repo/issues",
            'About': "Natural Language to SQL Agent for E-commerce Customer Support"
        }
    )

def apply_custom_css():
    """
    Apply custom CSS for modern, professional styling
    """
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom header styling */
    .custom-header {
        background: linear-gradient(90deg, #1f77b4 0%, #17becf 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Query input box styling */
    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 16px;
    }
    
    .stTextArea textarea:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 25px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Success message styling */
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Error message styling */
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Info box styling */
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Metrics styling */
    .metric-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    
    /* Code block styling */
    .sql-code {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        overflow-x: auto;
        margin: 1rem 0;
    }
    
    /* Loading animation */
    .loading-dots {
        display: inline-block;
    }
    
    .loading-dots:after {
        content: '...';
        animation: loading 1.5s infinite;
    }
    
    @keyframes loading {
        0%, 33% { content: '.'; }
        34%, 66% { content: '..'; }
        67%, 100% { content: '...'; }
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    """
    Display the main application header with modern styling
    """
    st.markdown("""
    <div class="custom-header">
        <h1>🤖 E-commerce SQL Agent</h1>
        <p style="margin: 0; font-size: 1.2rem; opacity: 0.9;">
            Natural Language Database Queries for Customer Support
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_system_status(health_data: Dict[str, Any]):
    """
    Display system status indicators in the sidebar
    
    Args:
        health_data: Health check data from backend
    """
    st.sidebar.markdown("### 🔍 System Status")
    
    # Database status
    db_status = "🟢 Connected" if health_data.get("database_connected") else "🔴 Disconnected"
    st.sidebar.markdown(f"**Database:** {db_status}")
    
    # LLM status  
    llm_status = "🟢 Available" if health_data.get("llm_available") else "🔴 Unavailable"
    st.sidebar.markdown(f"**LLM:** {llm_status}")
    
    # Uptime
    uptime = health_data.get("uptime_seconds", 0)
    uptime_formatted = f"{uptime/3600:.1f}h" if uptime > 3600 else f"{uptime/60:.1f}m"
    st.sidebar.markdown(f"**Uptime:** {uptime_formatted}")
    
    # Query count
    query_count = health_data.get("total_queries_processed", 0)
    st.sidebar.markdown(f"**Queries:** {query_count}")

def display_query_examples():
    """
    Display example queries in the sidebar for user inspiration
    """
    st.sidebar.markdown("### 💡 Example Queries")
    
    with st.sidebar.expander("Click to see examples", expanded=False):
        for i, example in enumerate(QUERY_EXAMPLES, 1):
            if st.button(f"📝 {example[:40]}...", key=f"example_{i}", use_container_width=True):
                st.session_state.selected_example = example

def create_metrics_dashboard(stats_data: Optional[Dict[str, Any]]):
    """
    Create a metrics dashboard showing API usage statistics
    
    Args:
        stats_data: Statistics data from the API
    """
    if not stats_data:
        st.info("📊 Statistics unavailable")
        return
    
    st.markdown("### 📊 Usage Statistics")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Queries",
            value=stats_data.get("total_queries_processed", 0),
            delta=None
        )
    
    with col2:
        success_rate = stats_data.get("success_rate", "0%")
        st.metric(
            label="Success Rate", 
            value=success_rate,
            delta=None
        )
    
    with col3:
        qpm = stats_data.get("queries_per_minute", 0)
        st.metric(
            label="Queries/Min",
            value=f"{qpm:.1f}",
            delta=None
        )
    
    with col4:
        uptime = stats_data.get("uptime_formatted", "0h")
        st.metric(
            label="Uptime",
            value=uptime,
            delta=None
        )

# ============================================================================
# RESPONSE FORMATTING FUNCTIONS
# ============================================================================

def format_sql_query(sql_query: str) -> str:
    """
    Format SQL query for better display with syntax highlighting
    
    Args:
        sql_query: Raw SQL query string
        
    Returns:
        str: Formatted SQL query
    """
    if not sql_query:
        return ""
    
    # Basic SQL formatting (simple approach)
    formatted = sql_query.replace(';', ';\n')
    formatted = formatted.replace(' FROM ', '\nFROM ')
    formatted = formatted.replace(' WHERE ', '\nWHERE ')
    formatted = formatted.replace(' JOIN ', '\nJOIN ')
    formatted = formatted.replace(' ORDER BY ', '\nORDER BY ')
    formatted = formatted.replace(' GROUP BY ', '\nGROUP BY ')
    
    return formatted.strip()

def display_query_response(response_data: Dict[str, Any]):
    """
    Display the query response in a user-friendly format
    
    Args:
        response_data: Response data from the API
    """
    if response_data.get("success"):
        # Success case
        st.markdown('<div class="success-message">', unsafe_allow_html=True)
        st.markdown("### ✅ Query Results")
        st.markdown(response_data.get("answer", "No answer provided"))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show execution details in expander
        with st.expander("🔍 Query Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                exec_time = response_data.get("execution_time", 0)
                st.metric("Execution Time", f"{exec_time:.3f}s")
                
            with col2:
                row_count = response_data.get("row_count", 0)
                st.metric("Rows Returned", row_count or "N/A")
            
            # Show SQL query
            if response_data.get("sql_query"):
                st.markdown("**Generated SQL Query:**")
                formatted_sql = format_sql_query(response_data["sql_query"])
                st.code(formatted_sql, language="sql")
    
    else:
        # Error case
        st.markdown('<div class="error-message">', unsafe_allow_html=True)
        st.markdown("### ❌ Query Failed")
        st.markdown(response_data.get("answer", "Unknown error occurred"))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show error details
        if response_data.get("error_message"):
            with st.expander("🔍 Error Details", expanded=False):
                st.error(response_data["error_message"])

def display_loading_message():
    """
    Display an animated loading message while processing query
    """
    placeholder = st.empty()
    
    messages = [
        "🤖 Understanding your question...",
        "🔍 Generating SQL query...",
        "🛡️ Validating query safety...",
        "🗃️ Executing database query...",
        "💬 Formatting response..."
    ]
    
    for message in messages:
        placeholder.markdown(f"**{message}**")
        time.sleep(0.8)
    
    placeholder.empty()

# ============================================================================
# SESSION STATE MANAGEMENT
# ============================================================================

def initialize_session_state():
    """
    Initialize Streamlit session state variables
    """
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    if 'selected_example' not in st.session_state:
        st.session_state.selected_example = ""
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{int(time.time())}"
    
    if 'backend_healthy' not in st.session_state:
        st.session_state.backend_healthy = False

def add_to_query_history(question: str, response: Dict[str, Any]):
    """
    Add a query and response to the session history
    
    Args:
        question: User's question
        response: API response data
    """
    history_item = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "question": question,
        "response": response,
        "success": response.get("success", False)
    }
    
    st.session_state.query_history.append(history_item)
    
    # Keep only last 10 items
    if len(st.session_state.query_history) > 10:
        st.session_state.query_history = st.session_state.query_history[-10:]

def display_query_history():
    """
    Display query history in the sidebar
    """
    if not st.session_state.query_history:
        return
    
    st.sidebar.markdown("### 📝 Recent Queries")
    
    with st.sidebar.expander("View History", expanded=False):
        for item in reversed(st.session_state.query_history):
            status_icon = "✅" if item["success"] else "❌"
            st.markdown(f"**{item['timestamp']}** {status_icon}")
            st.markdown(f"_{item['question'][:50]}..._")
            st.markdown("---")

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    'setup_page_config',
    'apply_custom_css', 
    'display_header',
    'check_backend_health',
    'send_query_to_backend',
    'display_system_status',
    'display_query_examples',
    'display_query_response',
    'display_loading_message',
    'initialize_session_state',
    'add_to_query_history',
    'display_query_history',
    'create_metrics_dashboard',
    'get_api_statistics'
]

# ============================================================================
# SUCCESS MESSAGE
# ============================================================================
print("=" * 60)
print("✅ Frontend utilities loaded successfully!")
print("   • Modern UI components ready")
print("   • API communication functions ready") 
print("   • Interactive features configured")
print("=" * 60)
