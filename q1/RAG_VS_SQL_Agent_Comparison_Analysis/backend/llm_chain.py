"""
LangChain LLM Chains for E-commerce SQL Agent

This module creates LangChain chains for:
1. Converting natural language to SQL queries (with PostgreSQL dialect)
2. Converting SQL results to human-readable responses

Uses Google Gemini 1.5 Flash with LangChain for structured interactions.

Author: SQL Agent Project
Date: July 19, 2025
"""

import logging
from typing import Dict, Any, Optional, Tuple
import re # Added for markdown code block cleaning

# LangChain imports
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough

# Import settings and tools
from settings import GOOGLE_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_MAX_TOKENS
from postgres import get_database_tools

# Set up logging
logger = logging.getLogger(__name__)

# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

# Template for converting natural language to SQL
SQL_GENERATION_TEMPLATE = """
You are an expert PostgreSQL database analyst for an e-commerce company.

Your task: Convert the user's natural language question into a valid PostgreSQL SQL query.

DATABASE SCHEMA:
{schema}

IMPORTANT RULES:
1. Generate ONLY PostgreSQL-compatible SQL queries
2. Use ONLY SELECT statements (no INSERT, UPDATE, DELETE, DROP, etc.)
3. Always use proper PostgreSQL syntax and functions
4. Include appropriate WHERE clauses to filter data
5. ALWAYS use JOINs to include descriptive information instead of just IDs:
   - For orders, JOIN with customers to show customer names
   - For reviews, JOIN with customers and products
   - For support tickets, JOIN with customers
6. Select specific columns that are meaningful to users (avoid showing raw IDs unless necessary)
7. Add LIMIT clauses for queries that might return many rows (max 100)
8. Use proper table and column names exactly as shown in the schema
9. For date comparisons, use PostgreSQL date functions
10. Return ONLY the raw SQL query - DO NOT wrap it in markdown code blocks or quotes
11. DO NOT include any explanations or comments

DIALECT: PostgreSQL

EXAMPLES:
Question: "Show all orders for John Doe"
SQL: SELECT o.order_date, o.status, o.total_amount, c.name, c.email FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE c.name = 'John Doe';

Question: "List cancelled orders"
SQL: SELECT c.name as customer_name, c.email, o.order_date, o.total_amount FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.status = 'cancelled';

Question: "Show product reviews"
SQL: SELECT c.name as reviewer, p.name as product_name, r.rating, r.comment, r.created_at FROM reviews r JOIN customers c ON r.customer_id = c.customer_id JOIN products p ON r.product_id = p.product_id ORDER BY r.created_at DESC LIMIT 100;

USER QUESTION: {question}

Generate only the SQL query, no explanations or code blocks:
"""

# Template for converting SQL results to human-readable responses
RESPONSE_GENERATION_TEMPLATE = """
You are a helpful customer service assistant for an e-commerce company.

Your task: Convert the SQL query results into a clear, friendly response for a customer service agent.

ORIGINAL QUESTION: {question}
SQL QUERY USED: {sql_query}
QUERY RESULTS: {query_results}

INSTRUCTIONS:
1. Write a natural, conversational response
2. Format the information in an easy-to-read way
3. Use customer names instead of IDs
4. Include relevant details like:
   - Order dates in a readable format (e.g., "July 18th, 2025")
   - Order status
   - Total amounts with currency symbol
   - Customer contact information when relevant
   - Product names and descriptions when relevant
5. If no results found, explain this clearly
6. Use friendly, professional tone
7. Keep the response concise but informative
8. NEVER show raw IDs in the response unless specifically asked
9. Group related information together
10. Use bullet points or lists for multiple items

Example Response Style:
"I found 2 cancelled orders from this month:

1. Customer: Jane Smith (jane.smith@email.com)
   • Order Date: July 15th, 2025
   • Items: Wireless Mouse
   • Total Amount: $49.99
   • Status: Cancelled

2. Customer: Mike Johnson
   • Order Date: July 12th, 2025
   • Items: Bluetooth Headphones
   • Total Amount: $129.99
   • Status: Cancelled"

Generate a helpful response:
"""

# ============================================================================
# LLM CHAIN CLASSES
# ============================================================================

class SQLGenerationChain:
    """
    LangChain chain for generating SQL queries from natural language
    """
    
    def __init__(self):
        """Initialize the SQL generation chain"""
        print("=" * 60)
        print("🔗 Initializing SQL Generation Chain")
        print(f"   Model: {GEMINI_MODEL}")
        print(f"   Temperature: {GEMINI_TEMPERATURE}")
        print("=" * 60)
        
        try:
            # Initialize Gemini LLM
            self.llm = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                temperature=GEMINI_TEMPERATURE,
                max_tokens=GEMINI_MAX_TOKENS,
                google_api_key=GOOGLE_API_KEY
            )
            
            # Create prompt template
            self.prompt = PromptTemplate(
                template=SQL_GENERATION_TEMPLATE,
                input_variables=["schema", "question"]
            )
            
            # Create the chain: prompt -> llm -> output parser
            self.chain = (
                self.prompt
                | self.llm
                | StrOutputParser()
            )
            
            print("✅ SQL Generation Chain initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SQL Generation Chain: {e}")
            print(f"❌ Failed to initialize SQL Generation Chain: {e}")
            raise
    
    def generate_sql(self, question: str, schema: str) -> str:
        """
        Generate SQL query from natural language question
        
        Args:
            question: Natural language question
            schema: Database schema information
            
        Returns:
            str: Generated SQL query
        """
        print("=" * 60)
        print("🤖 Generating SQL Query")
        print(f"   Question: {question[:80]}...")
        print("=" * 60)
        
        try:
            # Invoke the chain with input
            result = self.chain.invoke({
                "question": question,
                "schema": schema
            })
            
            # Clean up the result (remove extra whitespace, etc.)
            sql_query = result.strip()
            
            # Remove markdown code block syntax if present
            sql_query = re.sub(r'^```\w*\n', '', sql_query)  # Remove opening ```sql
            sql_query = re.sub(r'\n```$', '', sql_query)     # Remove closing ```
            sql_query = sql_query.strip()
            
            # Ensure query ends with semicolon
            if not sql_query.endswith(';'):
                sql_query += ';'
            
            print("✅ SQL query generated successfully")
            print(f"   Query: {sql_query[:100]}{'...' if len(sql_query) > 100 else ''}")
            print("=" * 60)
            
            return sql_query
            
        except Exception as e:
            error_msg = f"SQL generation failed: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            print("=" * 60)
            raise

class ResponseGenerationChain:
    """
    LangChain chain for generating human-readable responses from SQL results
    """
    
    def __init__(self):
        """Initialize the response generation chain"""
        print("=" * 60)
        print("🔗 Initializing Response Generation Chain")
        print("=" * 60)
        
        try:
            # Initialize Gemini LLM (with higher temperature for more natural responses)
            self.llm = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                temperature=0.3,  # Slightly higher for more natural language
                max_tokens=GEMINI_MAX_TOKENS,
                google_api_key=GOOGLE_API_KEY
            )
            
            # Create prompt template
            self.prompt = PromptTemplate(
                template=RESPONSE_GENERATION_TEMPLATE,
                input_variables=["question", "sql_query", "query_results"]
            )
            
            # Create the chain: prompt -> llm -> output parser
            self.chain = (
                self.prompt
                | self.llm
                | StrOutputParser()
            )
            
            print("✅ Response Generation Chain initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Response Generation Chain: {e}")
            print(f"❌ Failed to initialize Response Generation Chain: {e}")
            raise
    
    def generate_response(self, question: str, sql_query: str, query_results: str) -> str:
        """
        Generate human-readable response from SQL results
        
        Args:
            question: Original natural language question
            sql_query: SQL query that was executed
            query_results: Results from the SQL query
            
        Returns:
            str: Human-readable response
        """
        print("=" * 60)
        print("🤖 Generating Human-Readable Response")
        print(f"   Original question: {question[:60]}...")
        print(f"   Results length: {len(query_results)} characters")
        print("=" * 60)
        
        try:
            # Invoke the chain with input
            response = self.chain.invoke({
                "question": question,
                "sql_query": sql_query,
                "query_results": query_results
            })
            
            # Clean up the response
            formatted_response = response.strip()
            
            print("✅ Response generated successfully")
            print(f"   Response length: {len(formatted_response)} characters")
            print("=" * 60)
            
            return formatted_response
            
        except Exception as e:
            error_msg = f"Response generation failed: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            print("=" * 60)
            raise

# ============================================================================
# MAIN CHAIN MANAGER
# ============================================================================

class LLMChainManager:
    """
    Manager class that coordinates SQL generation and response formatting chains
    """
    
    def __init__(self):
        """Initialize the LLM chain manager"""
        print("=" * 80)
        print("🚀 INITIALIZING LLM CHAIN MANAGER")
        print("=" * 80)
        
        try:
            # Initialize both chains
            self.sql_chain = SQLGenerationChain()
            self.response_chain = ResponseGenerationChain()
            
            # Get database tools for schema information
            self.db_tools = get_database_tools()
            
            if not self.db_tools:
                raise Exception("Database tools not available")
            
            print("=" * 80)
            print("✅ LLM CHAIN MANAGER READY!")
            print("   • SQL Generation Chain: ✅")
            print("   • Response Generation Chain: ✅")
            print("   • Database Tools: ✅")
            print("=" * 80)
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM Chain Manager: {e}")
            print(f"❌ LLM Chain Manager initialization failed: {e}")
            print("=" * 80)
            raise
    
    def process_question(self, question: str) -> Tuple[str, str]:
        """
        Process a natural language question through the complete chain
        
        Args:
            question: Natural language question from user
            
        Returns:
            Tuple[str, str]: (generated_sql_query, schema_info)
        """
        print("=" * 80)
        print("🔄 PROCESSING NATURAL LANGUAGE QUESTION")
        print(f"   Question: {question}")
        print("=" * 80)
        
        try:
            # Step 1: Get database schema information
            print("📊 Step 1: Retrieving database schema...")
            schema_info = self.db_tools.get_schema_info()
            
            # Step 2: Generate SQL query
            print("🤖 Step 2: Generating SQL query...")
            sql_query = self.sql_chain.generate_sql(question, schema_info)
            
            return sql_query, schema_info
            
        except Exception as e:
            error_msg = f"Question processing failed: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            print("=" * 80)
            raise
    
    def format_response(self, question: str, sql_query: str, query_results: str) -> str:
        """
        Format SQL query results into human-readable response
        
        Args:
            question: Original question
            sql_query: SQL query that was executed
            query_results: Results from query execution
            
        Returns:
            str: Formatted human-readable response
        """
        return self.response_chain.generate_response(question, sql_query, query_results)

# ============================================================================
# GLOBAL CHAIN MANAGER INSTANCE
# ============================================================================

# Initialize global chain manager
print("=" * 80)
print("🤖 INITIALIZING GLOBAL LLM CHAINS")
print("=" * 80)

try:
    chain_manager = LLMChainManager()
    print("✅ Global LLM Chain Manager ready for use")
except Exception as e:
    print(f"❌ Failed to initialize global LLM chains: {e}")
    chain_manager = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_chain_manager() -> Optional[LLMChainManager]:
    """
    Get the global LLM chain manager instance
    
    Returns:
        LLMChainManager: The initialized chain manager
    """
    return chain_manager

def is_chains_ready() -> bool:
    """
    Check if LLM chains are ready for use
    
    Returns:
        bool: True if chains are ready, False otherwise
    """
    return chain_manager is not None

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    'SQLGenerationChain',
    'ResponseGenerationChain', 
    'LLMChainManager',
    'get_chain_manager',
    'is_chains_ready'
]

# ============================================================================
# TEST FUNCTION
# ============================================================================

def test_chains():
    """Test the LLM chains with a sample question"""
    if not chain_manager:
        print("❌ Chain manager not initialized")
        return
    
    print("=" * 80)
    print("🧪 TESTING LLM CHAINS")
    print("=" * 80)
    
    try:
        # Test question
        test_question = "Show all customers with their email addresses"
        
        # Generate SQL
        sql_query, schema = chain_manager.process_question(test_question)
        print(f"✅ Generated SQL: {sql_query}")
        
        # Test response generation (with mock results)
        mock_results = "customer_id | name | email\n1 | John Doe | john@email.com"
        response = chain_manager.format_response(test_question, sql_query, mock_results)
        print(f"✅ Generated Response: {response}")
        
        print("=" * 80)
        print("🎉 LLM CHAINS TEST COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Chain test failed: {e}")

if __name__ == "__main__":
    test_chains()
