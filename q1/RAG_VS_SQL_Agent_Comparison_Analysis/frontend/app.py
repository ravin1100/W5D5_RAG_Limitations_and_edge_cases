"""
Main Streamlit Application for E-commerce SQL Agent

This is the main Streamlit application that provides an interactive, modern
frontend interface for customer support agents to query the e-commerce
database using natural language. Features real-time processing, query
history, and comprehensive system monitoring.

Author: SQL Agent Project
Date: July 19, 2025
"""

import streamlit as st
import time
import asyncio
from datetime import datetime
import pandas as pd


# Import our utility functions
from utils import (
    setup_page_config, apply_custom_css, display_header,
    check_backend_health, send_query_to_backend, display_system_status,
    display_query_examples, display_query_response, display_loading_message,
    initialize_session_state, add_to_query_history, display_query_history,
    create_metrics_dashboard, get_api_statistics, QUERY_EXAMPLES
)

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

def configure_application():
    """
    Configure the Streamlit application with page settings and styling
    """
    print("=" * 80)
    print("🎨 CONFIGURING STREAMLIT APPLICATION")
    print("=" * 80)
    
    # Set up page configuration
    setup_page_config()
    
    # Apply custom CSS styling
    apply_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    print("✅ Application configuration completed")
    print("=" * 80)

# ============================================================================
# MAIN APPLICATION INTERFACE
# ============================================================================

def render_main_interface():
    """
    Render the main application interface with all components
    """
    # Display the header
    display_header()
    
    # Check backend health
    is_healthy, health_data = check_backend_health()
    st.session_state.backend_healthy = is_healthy
    
    # Show connection status
    # if is_healthy:
    #     st.success("🟢 **Backend Connected** - Ready to process queries")
    # else:
    #     st.error("🔴 **Backend Disconnected** - Please check if the backend server is running")
    #     st.info("💡 **Tip:** Make sure to run `python backend/main.py` to start the backend server")
    #     return
    
    # Main query interface
    render_query_interface()
    
    # Display statistics dashboard
    render_statistics_section()

def render_query_interface():
    """
    Render the main query input and response interface
    """
    st.markdown("### 🎯 Ask Your Question")
    
    # Create columns for better layout
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Main query input
        query_input = st.text_area(
            label="Enter your natural language question:",
            placeholder="Example: Show all customers who placed orders in the last 7 days",
            height=100,
            help="Ask questions about customers, orders, products, reviews, or support tickets",
            key="main_query_input"
        )
        
        # Use example query if selected
        if st.session_state.selected_example:
            query_input = st.session_state.selected_example
            st.session_state.selected_example = ""  # Reset after use
    
    with col2:
        st.markdown("#### 🚀 Actions")
        
        # Submit button with enhanced styling
        submit_clicked = st.button(
            "🔍 Process Query",
            type="primary",
            use_container_width=True,
            help="Send your question to the SQL Agent"
        )
        
        # Clear button
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.main_query_input = ""
            st.rerun()
        
        # Random example button
        if st.button("🎲 Random Example", use_container_width=True):
            import random
            st.session_state.selected_example = random.choice(QUERY_EXAMPLES)
            st.rerun()
    
    # Process query if submitted
    if submit_clicked and query_input.strip():
        process_user_query(query_input.strip())
    elif submit_clicked:
        st.warning("⚠️ Please enter a question before submitting")

def process_user_query(question: str):
    """
    Process a user query through the backend API with real-time feedback
    
    Args:
        question: User's natural language question
    """
    print("=" * 100)
    print("🚀 PROCESSING USER QUERY IN FRONTEND")
    print(f"   Question: {question}")
    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 100)
    
    # Show processing indicator
    with st.spinner("🤖 Processing your question..."):
        # Add some visual feedback
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate processing stages with progress updates
        processing_steps = [
            (20, "🤖 Understanding your question..."),
            (40, "🔍 Generating SQL query..."),
            (60, "🛡️ Validating query safety..."),
            (80, "🗃️ Executing database query..."),
            (100, "💬 Formatting response...")
        ]
        
        for progress, message in processing_steps:
            progress_bar.progress(progress)
            status_text.markdown(f"**{message}**")
            time.sleep(0.3)
        
        # Send query to backend
        response_data = send_query_to_backend(question, st.session_state.user_id)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
    
    # Display response
    display_query_response(response_data)
    
    # Add to query history
    add_to_query_history(question, response_data)
    
    # Show follow-up suggestions if successful
    if response_data.get("success"):
        show_followup_suggestions(question)

def show_followup_suggestions(original_question: str):
    """
    Show relevant follow-up question suggestions based on the original query
    
    Args:
        original_question: The original question asked by the user
    """
    st.markdown("### 💡 Follow-up Suggestions")
    
    # Generate contextual suggestions based on keywords
    suggestions = []
    
    if "customer" in original_question.lower():
        suggestions.extend([
            "Show order history for this customer",
            "Find support tickets for this customer",
            "List reviews by this customer"
        ])
    
    if "order" in original_question.lower():
        suggestions.extend([
            "Show customer details for these orders",
            "Find related support tickets",
            "Check payment status for these orders"
        ])
    
    if "product" in original_question.lower():
        suggestions.extend([
            "Show reviews for this product",
            "Check current stock levels",
            "Find customers who bought this product"
        ])
    
    if "support" in original_question.lower():
        suggestions.extend([
            "Show customer details for these tickets",
            "Find related orders",
            "Check resolution time statistics"
        ])
    
    # Display suggestions as clickable buttons
    if suggestions:
        cols = st.columns(min(len(suggestions), 3))
        for i, suggestion in enumerate(suggestions[:6]):  # Limit to 6 suggestions
            with cols[i % 3]:
                if st.button(f"➡️ {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                    st.session_state.selected_example = suggestion
                    st.rerun()

def render_statistics_section():
    """
    Render the statistics and monitoring section
    """
    st.markdown("---")
    
    # Get and display statistics
    stats_data = get_api_statistics()
    create_metrics_dashboard(stats_data)
    
    # Advanced statistics in expandable section
    with st.expander("📊 Advanced Statistics", expanded=False):
        if stats_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### System Health")
                system_status = stats_data.get("system_status", {})
                
                st.markdown(f"**Database:** {'🟢 Ready' if system_status.get('database_ready') else '🔴 Not Ready'}")
                st.markdown(f"**LLM Chains:** {'🟢 Ready' if system_status.get('llm_chains_ready') else '🔴 Not Ready'}")
                st.markdown(f"**Agent:** {'🟢 Ready' if system_status.get('agent_ready') else '🔴 Not Ready'}")
            
            with col2:
                st.markdown("#### Performance Metrics")
                st.markdown(f"**Successful Queries:** {stats_data.get('successful_queries', 0)}")
                st.markdown(f"**Failed Queries:** {stats_data.get('failed_queries', 0)}")
                st.markdown(f"**Queries/Minute:** {stats_data.get('queries_per_minute', 0):.2f}")
        else:
            st.info("📊 Statistics not available")

# ============================================================================
# SIDEBAR INTERFACE
# ============================================================================

def render_sidebar():
    """
    Render the sidebar with system status, examples, and history
    """
    st.sidebar.title("🤖 SQL Agent")
    st.sidebar.markdown("---")
    
    # System status section
    if st.session_state.backend_healthy:
        is_healthy, health_data = check_backend_health()
        display_system_status(health_data)
    else:
        st.sidebar.error("🔴 Backend Offline")
    
    st.sidebar.markdown("---")
    
    # Query examples section
    display_query_examples()
    
    st.sidebar.markdown("---")
    
    # Query history section
    display_query_history()
    
    st.sidebar.markdown("---")
    
    # Settings and info section
    render_sidebar_settings()

def render_sidebar_settings():
    """
    Render settings and information in the sidebar
    """
    st.sidebar.markdown("### ⚙️ Settings")
    
    # User ID display and modification
    with st.sidebar.expander("👤 User Settings", expanded=False):
        current_user = st.session_state.get('user_id', 'Unknown')
        st.markdown(f"**Current User ID:** `{current_user}`")
        
        new_user_id = st.text_input(
            "Change User ID:",
            value=current_user,
            help="Used for tracking queries in logs"
        )
        
        if new_user_id != current_user:
            st.session_state.user_id = new_user_id
            st.success("✅ User ID updated!")
    
    # Application info
    with st.sidebar.expander("ℹ️ About", expanded=False):
        st.markdown("""
        **E-commerce SQL Agent v1.0**
        
        This application converts natural language questions 
        into SQL queries for the e-commerce database.
        
        **Features:**
        - 🤖 AI-powered query generation
        - 🛡️ SQL injection prevention
        - 📊 Real-time statistics
        - 📝 Query history tracking
        - 🎯 Interactive examples
        
        **Support:**
        - Ask questions about customers, orders, products
        - Get support ticket information
        - View reviews and ratings
        """)

# ============================================================================
# ERROR HANDLING AND RECOVERY
# ============================================================================

def handle_application_error(error: Exception):
    """
    Handle application-level errors gracefully
    
    Args:
        error: Exception that occurred
    """
    st.error("🚨 **Application Error**")
    st.error(f"An unexpected error occurred: {str(error)}")
    
    with st.expander("🔍 Error Details", expanded=False):
        st.code(str(error))
    
    st.info("💡 **Troubleshooting Tips:**")
    st.markdown("""
    - Check if the backend server is running
    - Verify your internet connection
    - Try refreshing the page
    - Contact support if the problem persists
    """)

# ============================================================================
# MAIN APPLICATION ENTRY POINT
# ============================================================================

def main():
    """
    Main application entry point
    """
    try:
        print("=" * 100)
        print("🚀 STARTING E-COMMERCE SQL AGENT FRONTEND")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
        
        # Configure the application
        configure_application()
        
        # Render sidebar
        render_sidebar()
        
        # Render main interface
        render_main_interface()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666; padding: 1rem;'>"
            "🤖 E-commerce SQL Agent | Built with Streamlit, FastAPI, and LangChain"
            "</div>",
            unsafe_allow_html=True
        )
        
        print("✅ Frontend application rendered successfully")
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        handle_application_error(e)

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == "__main__":
    """
    Run the Streamlit application
    """
    print("=" * 100)
    print("🎨 INITIALIZING STREAMLIT APPLICATION")
    print("=" * 100)
    
    main()
