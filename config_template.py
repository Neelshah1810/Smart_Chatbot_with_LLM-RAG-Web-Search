"""
Configuration Template for Advanced Users
Copy this to config.py and customize as needed
"""

# ==================== LLM CONFIGURATION ====================

# Groq Model Settings
LLM_CONFIG = {
    "model_name": "llama-3.1-70b-versatile",  # Options: llama-3.1-70b-versatile, mixtral-8x7b-32768
    "temperature": 0.7,  # 0.0 = deterministic, 1.0 = creative
    "max_tokens": 2048,  # Maximum response length
}

# Alternative: Use different model for routing
ROUTING_LLM_CONFIG = {
    "model_name": "llama-3.1-70b-versatile",
    "temperature": 0.1,  # Lower temperature for more consistent routing
}

# ==================== EMBEDDINGS CONFIGURATION ====================

EMBEDDINGS_CONFIG = {
    "model_name": "sentence-transformers/all-MiniLM-L6-v2",
    # Alternatives:
    # "sentence-transformers/all-mpnet-base-v2" - Better quality, slower
    # "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" - Multilingual
}

# ==================== DOCUMENT PROCESSING ====================

TEXT_SPLITTER_CONFIG = {
    "chunk_size": 1000,  # Characters per chunk
    "chunk_overlap": 200,  # Overlap between chunks
    "separators": ["\n\n", "\n", " ", ""],  # Split hierarchy
}

# Supported file types
SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx"]

# Maximum file size (in MB)
MAX_FILE_SIZE_MB = 10

# ==================== RAG CONFIGURATION ====================

RAG_CONFIG = {
    "retriever_k": 4,  # Number of documents to retrieve
    "return_source_documents": True,
    "max_sources_to_display": 3,
}

# ==================== WEB SEARCH CONFIGURATION ====================

WEB_SEARCH_CONFIG = {
    "max_results": 5,  # Number of search results to consider
    "region": "wt-wt",  # Region: wt-wt (worldwide), us-en (US), uk-en (UK)
    "safe_search": "moderate",  # Options: off, moderate, strict
}

# ==================== MEMORY CONFIGURATION ====================

MEMORY_CONFIG = {
    "memory_type": "buffer",  # Options: buffer, summary, buffer_window
    "max_token_limit": 4000,  # Maximum tokens to keep in memory
    "return_messages": True,
}

# Context window for LLM route (number of previous exchanges to include)
CONTEXT_WINDOW_SIZE = 3  # Last 3 exchanges (6 messages)

# ==================== ROUTING CONFIGURATION ====================

# Routing keywords for better accuracy
ROUTING_KEYWORDS = {
    "rag": [
        "document", "file", "pdf", "uploaded", "in the text",
        "according to", "from the", "what does it say", "in the paper",
        "the article states", "summarize the", "extract from"
    ],
    "web": [
        "latest", "current", "today", "now", "recent", "news",
        "weather", "stock", "price", "happening", "2024", "2025",
        "live", "real-time", "update", "breaking"
    ],
    "llm": [
        "hello", "hi", "thanks", "thank you", "bye", "how are you",
        "explain", "what is", "how does", "why", "tell me about"
    ]
}

# Force routing for specific patterns (overrides LLM decision)
FORCE_ROUTING = True

# Minimum confidence threshold for routing (0.0 to 1.0)
ROUTING_CONFIDENCE_THRESHOLD = 0.6

# ==================== UI CONFIGURATION ====================

UI_CONFIG = {
    "page_title": "AI Chatbot with RAG & Web Search",
    "page_icon": "🤖",
    "layout": "wide",
    "sidebar_width": 300,
}

# Color scheme for route badges
ROUTE_COLORS = {
    "llm": "#4caf50",  # Green
    "rag": "#2196f3",  # Blue
    "web": "#ff9800",  # Orange
}

# Route emojis
ROUTE_EMOJIS = {
    "llm": "🟢",
    "rag": "🔵",
    "web": "🟠",
}

# ==================== PERFORMANCE CONFIGURATION ====================

PERFORMANCE_CONFIG = {
    "batch_size": 32,  # Batch size for embeddings
    "use_cache": True,  # Cache embeddings
    "lazy_load": True,  # Lazy load documents
}

# Enable/disable features
FEATURES = {
    "web_search": True,
    "rag": True,
    "conversation_memory": True,
    "source_citation": True,
    "route_visualization": True,
}

# ==================== LOGGING CONFIGURATION ====================

LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "log_file": "chatbot.log",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}

# ==================== ADVANCED SETTINGS ====================

ADVANCED_SETTINGS = {
    # Retry settings for API calls
    "max_retries": 3,
    "retry_delay": 1,  # seconds
    
    # Timeout settings
    "llm_timeout": 30,  # seconds
    "web_search_timeout": 10,  # seconds
    
    # Rate limiting
    "rate_limit_calls": 100,
    "rate_limit_period": 60,  # seconds
    
    # Error handling
    "fallback_to_llm": True,  # Fallback to LLM if other routes fail
    "show_error_details": False,  # Show detailed errors to users
}

# ==================== PROMPT TEMPLATES ====================

# Custom prompt for routing (optional)
ROUTING_PROMPT_TEMPLATE = """You are a query routing expert. Analyze the user query and determine the best source.

Query: "{query}"
Documents available: {has_documents}
Chat history: {chat_history}

Route to:
- RAG: if asking about uploaded documents
- WEB: if asking about current/recent information
- LLM: for general conversation and knowledge

Respond with only: RAG, WEB, or LLM"""

# Custom prompt for RAG synthesis (optional)
RAG_SYNTHESIS_PROMPT = """Use the following context from documents to answer the question.
Be specific and cite sources when possible.

Context: {context}

Question: {question}

Answer:"""

# Custom prompt for web search synthesis (optional)
WEB_SYNTHESIS_PROMPT = """Based on the web search results, provide a comprehensive answer.

Query: {query}

Search Results:
{results}

Synthesize a clear, accurate answer:"""

# ==================== USAGE NOTES ====================

"""
HOW TO USE THIS CONFIG:

1. Copy this file to 'config.py' in the same directory as chatbot_app.py

2. Modify the settings as needed

3. In chatbot_app.py, import your config:
   from config import *

4. Replace hardcoded values with config variables

EXAMPLE MODIFICATIONS:

# For more creative responses:
LLM_CONFIG["temperature"] = 1.0

# For better document retrieval:
RAG_CONFIG["retriever_k"] = 8

# For multilingual support:
EMBEDDINGS_CONFIG["model_name"] = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# For faster processing (fewer chunks):
TEXT_SPLITTER_CONFIG["chunk_size"] = 1500

# For more context in conversations:
CONTEXT_WINDOW_SIZE = 5
"""
