"""
SQL Agent using LangGraph for E-commerce Natural Language Queries

This module creates a LangGraph-based agent that orchestrates the complete 
workflow of natural language to SQL conversion, validation, execution, 
and response formatting with retry logic.

Author: SQL Agent Project
Date: July 19, 2025
"""

import logging
import time
from typing import Dict, Any, Optional, List
from enum import Enum

# LangGraph imports
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

# Import our modules
from llm_chain import get_chain_manager
from sql_validator import validate_sql_query
from postgres import get_database_tools
from models import QueryResponse, ErrorResponse
from settings import MAX_SQL_RETRIES

# Set up logging
logger = logging.getLogger(__name__)

# ============================================================================
# AGENT STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """
    State structure for the SQL Agent workflow
    
    This defines all the data that flows through the agent's decision process
    """
    # Input
    question: str                    # Original user question
    user_id: Optional[str]          # User ID for tracking
    
    # Processing state
    current_attempt: int            # Current retry attempt number
    sql_query: Optional[str]        # Generated SQL query
    validation_result: Optional[Dict[str, Any]]  # SQL validation result
    query_results: Optional[str]    # Results from database query
    execution_success: bool         # Whether SQL executed successfully
    
    # Output
    final_response: Optional[str]   # Final human-readable response
    error_message: Optional[str]    # Error message if something failed
    
    # Metadata
    start_time: float              # When processing started
    total_execution_time: Optional[float]  # Total time taken
    row_count: Optional[int]       # Number of rows returned

class WorkflowStatus(Enum):
    """Status indicators for workflow steps"""
    PENDING = "pending"
    SUCCESS = "success" 
    FAILED = "failed"
    RETRY_NEEDED = "retry_needed"

# ============================================================================
# WORKFLOW NODES
# ============================================================================

def initialize_state(state: AgentState) -> AgentState:
    """
    Initialize the agent state with default values
    
    This is the entry point of the workflow
    """
    print("=" * 80)
    print("🚀 INITIALIZING SQL AGENT WORKFLOW")
    print(f"   Question: {state['question']}")
    print(f"   User ID: {state.get('user_id', 'Anonymous')}")
    print("=" * 80)
    
    state.update({
        "current_attempt": 1,
        "sql_query": None,
        "validation_result": None,
        "query_results": None,
        "execution_success": False,
        "final_response": None,
        "error_message": None,
        "start_time": time.time(),
        "total_execution_time": None,
        "row_count": None
    })
    
    return state

def generate_sql_node(state: AgentState) -> AgentState:
    """
    Generate SQL query from natural language question
    """
    print("=" * 60)
    print(f"🤖 STEP 1: GENERATING SQL QUERY (Attempt {state['current_attempt']})")
    print("=" * 60)
    
    try:
        # Get chain manager
        chain_manager = get_chain_manager()
        if not chain_manager:
            state["error_message"] = "LLM chains not available"
            return state
        
        # Generate SQL query
        sql_query, schema_info = chain_manager.process_question(state["question"])
        
        state["sql_query"] = sql_query
        print(f"✅ SQL generated: {sql_query[:100]}...")
        
    except Exception as e:
        error_msg = f"SQL generation failed: {str(e)}"
        logger.error(error_msg)
        state["error_message"] = error_msg
        print(f"❌ {error_msg}")
    
    print("=" * 60)
    return state

def validate_sql_node(state: AgentState) -> AgentState:
    """
    Validate the generated SQL query for safety and correctness
    """
    print("=" * 60)
    print("🛡️  STEP 2: VALIDATING SQL QUERY")
    print("=" * 60)
    
    try:
        if not state["sql_query"]:
            state["error_message"] = "No SQL query to validate"
            return state
        
        # Validate SQL query
        validation_result = validate_sql_query(state["sql_query"])
        
        state["validation_result"] = {
            "is_valid": validation_result.is_valid,
            "error_message": validation_result.error_message,
            "warnings": validation_result.warnings
        }
        
        if validation_result.is_valid:
            print("✅ SQL query validation passed")
        else:
            print(f"❌ SQL validation failed: {validation_result.error_message}")
        
    except Exception as e:
        error_msg = f"SQL validation failed: {str(e)}"
        logger.error(error_msg)
        state["error_message"] = error_msg
        print(f"❌ {error_msg}")
    
    print("=" * 60)
    return state

def execute_sql_node(state: AgentState) -> AgentState:
    """
    Execute the validated SQL query against the database
    """
    print("=" * 60)
    print("🗃️  STEP 3: EXECUTING SQL QUERY")
    print("=" * 60)
    
    try:
        if not state["sql_query"]:
            state["error_message"] = "No SQL query to execute"
            return state
        
        # Get database tools
        db_tools = get_database_tools()
        if not db_tools:
            state["error_message"] = "Database tools not available"
            return state
        
        # Execute SQL query
        success, results, row_count = db_tools.execute_query(state["sql_query"])
        
        state["execution_success"] = success
        state["query_results"] = results
        state["row_count"] = row_count
        
        if success:
            print(f"✅ Query executed successfully")
            print(f"   Rows returned: {row_count}")
        else:
            print(f"❌ Query execution failed: {results}")
            # If execution failed, we might want to retry with a new SQL query
            
    except Exception as e:
        error_msg = f"SQL execution failed: {str(e)}"
        logger.error(error_msg)
        state["error_message"] = error_msg
        state["execution_success"] = False
        print(f"❌ {error_msg}")
    
    print("=" * 60)
    return state

def format_response_node(state: AgentState) -> AgentState:
    """
    Format the query results into a human-readable response
    """
    print("=" * 60)
    print("💬 STEP 4: FORMATTING RESPONSE")
    print("=" * 60)
    
    try:
        if not state["execution_success"] or not state["query_results"]:
            state["error_message"] = "No valid query results to format"
            return state
        
        # Get chain manager
        chain_manager = get_chain_manager()
        if not chain_manager:
            state["error_message"] = "LLM chains not available for response formatting"
            return state
        
        # Format response
        response = chain_manager.format_response(
            question=state["question"],
            sql_query=state["sql_query"],
            query_results=state["query_results"]
        )
        
        state["final_response"] = response
        print(f"✅ Response formatted successfully")
        print(f"   Response length: {len(response)} characters")
        
    except Exception as e:
        error_msg = f"Response formatting failed: {str(e)}"
        logger.error(error_msg)
        state["error_message"] = error_msg
        print(f"❌ {error_msg}")
    
    print("=" * 60)
    return state

def finalize_state_node(state: AgentState) -> AgentState:
    """
    Finalize the state and calculate execution metrics
    """
    print("=" * 60)
    print("🎯 FINALIZING WORKFLOW")
    print("=" * 60)
    
    # Calculate total execution time
    state["total_execution_time"] = time.time() - state["start_time"]
    
    print(f"   Total execution time: {state['total_execution_time']:.3f} seconds")
    print(f"   Attempts made: {state['current_attempt']}")
    print(f"   Success: {state['final_response'] is not None}")
    print("=" * 60)
    
    return state

def increment_retry_node(state: AgentState) -> AgentState:
    """
    Increment retry counter and prepare for another attempt
    """
    state["current_attempt"] += 1
    
    print("=" * 60)
    print(f"🔄 PREPARING RETRY ATTEMPT {state['current_attempt']}")
    print("   Previous attempt failed, trying again...")
    print("=" * 60)
    
    # Reset state for retry
    state["sql_query"] = None
    state["validation_result"] = None
    state["query_results"] = None
    state["execution_success"] = False
    
    return state

# ============================================================================
# DECISION FUNCTIONS
# ============================================================================

def should_validate_sql(state: AgentState) -> str:
    """
    Decide whether to proceed with SQL validation
    """
    if state.get("error_message") or not state.get("sql_query"):
        return "error"
    return "validate"

def should_execute_sql(state: AgentState) -> str:
    """
    Decide whether to proceed with SQL execution
    """
    if state.get("error_message"):
        return "error"
    
    validation_result = state.get("validation_result", {})
    if not validation_result.get("is_valid", False):
        return "retry_or_error"
    
    return "execute"

def should_format_response(state: AgentState) -> str:
    """
    Decide whether to proceed with response formatting
    """
    if state.get("error_message"):
        return "error"
    
    if not state.get("execution_success"):
        return "retry_or_error"
    
    return "format"

def should_retry_or_end(state: AgentState) -> str:
    """
    Decide whether to retry or end with error
    """
    if state["current_attempt"] < MAX_SQL_RETRIES:
        return "retry"
    return "error"

# ============================================================================
# SQL AGENT CLASS
# ============================================================================

class SQLAgent:
    """
    LangGraph-based SQL Agent for natural language database queries
    """
    
    def __init__(self):
        """Initialize the SQL Agent with workflow graph"""
        print("=" * 80)
        print("🤖 INITIALIZING SQL AGENT")
        print("=" * 80)
        
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()
        
        print("✅ SQL Agent initialized successfully")
        print(f"   Max retries: {MAX_SQL_RETRIES}")
        print("=" * 80)
    
    def _create_workflow(self) -> StateGraph:
        """
        Create the LangGraph workflow for SQL processing
        """
        print("🔧 Creating workflow graph...")
        
        # Create workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("initialize", initialize_state)
        workflow.add_node("generate_sql", generate_sql_node)
        workflow.add_node("validate_sql", validate_sql_node)
        workflow.add_node("execute_sql", execute_sql_node)
        workflow.add_node("format_response", format_response_node)
        workflow.add_node("finalize", finalize_state_node)
        workflow.add_node("increment_retry", increment_retry_node)
        
        # Define workflow edges
        workflow.set_entry_point("initialize")
        
        workflow.add_edge("initialize", "generate_sql")
        
        workflow.add_conditional_edges(
            "generate_sql",
            should_validate_sql,
            {
                "validate": "validate_sql",
                "error": "finalize"
            }
        )
        
        workflow.add_conditional_edges(
            "validate_sql",
            should_execute_sql,
            {
                "execute": "execute_sql",
                "retry_or_error": "increment_retry",
                "error": "finalize"
            }
        )
        
        workflow.add_conditional_edges(
            "execute_sql",
            should_format_response,
            {
                "format": "format_response",
                "retry_or_error": "increment_retry",
                "error": "finalize"
            }
        )
        
        workflow.add_edge("format_response", "finalize")
        
        workflow.add_conditional_edges(
            "increment_retry",
            should_retry_or_end,
            {
                "retry": "generate_sql",
                "error": "finalize"
            }
        )
        
        workflow.add_edge("finalize", END)
        
        print("✅ Workflow graph created successfully")
        return workflow
    
    def process_query(self, question: str, user_id: Optional[str] = None) -> QueryResponse:
        """
        Process a natural language query through the complete workflow
        
        Args:
            question: Natural language question
            user_id: Optional user ID for tracking
            
        Returns:
            QueryResponse: Complete response with results or error information
        """
        print("=" * 100)
        print("🚀 STARTING SQL AGENT QUERY PROCESSING")
        print(f"   Question: {question}")
        print("=" * 100)
        
        try:
            # Initialize state
            initial_state: AgentState = {
                "question": question,
                "user_id": user_id,
                "current_attempt": 0,
                "sql_query": None,
                "validation_result": None,
                "query_results": None,
                "execution_success": False,
                "final_response": None,
                "error_message": None,
                "start_time": time.time(),
                "total_execution_time": None,
                "row_count": None
            }
            
            # Execute workflow
            final_state = self.app.invoke(initial_state)
            
            # Create response
            if final_state.get("final_response"):
                # Success case
                response = QueryResponse(
                    success=True,
                    answer=final_state["final_response"],
                    sql_query=final_state.get("sql_query"),
                    row_count=final_state.get("row_count"),
                    execution_time=final_state.get("total_execution_time"),
                    error_message=None
                )
                
                print("=" * 100)
                print("🎉 QUERY PROCESSING COMPLETED SUCCESSFULLY!")
                print(f"   Execution time: {response.execution_time:.3f}s")
                print(f"   Rows returned: {response.row_count}")
                print("=" * 100)
                
            else:
                # Error case
                error_message = final_state.get("error_message", "Unknown error occurred")
                response = QueryResponse(
                    success=False,
                    answer=f"I apologize, but I couldn't process your question: {error_message}",
                    sql_query=final_state.get("sql_query"),
                    row_count=None,
                    execution_time=final_state.get("total_execution_time"),
                    error_message=error_message
                )
                
                print("=" * 100)
                print("❌ QUERY PROCESSING FAILED")
                print(f"   Error: {error_message}")
                print(f"   Attempts made: {final_state.get('current_attempt', 0)}")
                print("=" * 100)
            
            return response
            
        except Exception as e:
            error_msg = f"Agent workflow failed: {str(e)}"
            logger.error(error_msg)
            
            print("=" * 100)
            print("💥 CRITICAL ERROR IN SQL AGENT")
            print(f"   Error: {error_msg}")
            print("=" * 100)
            
            return QueryResponse(
                success=False,
                answer="I encountered a technical error while processing your question. Please try again later.",
                sql_query=None,
                row_count=None,
                execution_time=None,
                error_message=error_msg
            )

# ============================================================================
# GLOBAL AGENT INSTANCE
# ============================================================================

# Initialize global SQL agent
print("=" * 80)
print("🤖 INITIALIZING GLOBAL SQL AGENT")
print("=" * 80)

try:
    sql_agent = SQLAgent()
    print("✅ Global SQL Agent ready for use")
except Exception as e:
    print(f"❌ Failed to initialize SQL Agent: {e}")
    sql_agent = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_sql_agent() -> Optional[SQLAgent]:
    """
    Get the global SQL agent instance
    
    Returns:
        SQLAgent: The initialized SQL agent
    """
    return sql_agent

def is_agent_ready() -> bool:
    """
    Check if SQL agent is ready for use
    
    Returns:
        bool: True if agent is ready, False otherwise
    """
    return sql_agent is not None

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    'SQLAgent',
    'AgentState',
    'WorkflowStatus',
    'get_sql_agent',
    'is_agent_ready'
]

# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_agent():
    """Test the SQL agent with a sample query"""
    if not sql_agent:
        print("❌ SQL Agent not initialized")
        return
    
    print("=" * 80)
    print("🧪 TESTING SQL AGENT")
    print("=" * 80)
    
    try:
        # Test query
        test_question = "Show me all customers"
        response = sql_agent.process_query(test_question, "test_user")
        
        print(f"✅ Test completed")
        print(f"   Success: {response.success}")
        print(f"   Answer: {response.answer[:100]}...")
        if response.sql_query:
            print(f"   SQL: {response.sql_query}")
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")

if __name__ == "__main__":
    test_agent()
