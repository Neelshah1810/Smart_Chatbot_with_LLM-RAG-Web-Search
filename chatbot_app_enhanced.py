"""
Enhanced Chatbot Application with Additional Features
This version includes improved error handling, logging, and performance optimizations
"""

import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
import tempfile
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Chatbot Pro - RAG & Web Search",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
st.markdown("""
<style>
    /* Hide the hamburger menu */
    button[title="View menu"] {
        display: none !important;
    }
    
    /* Hide the sidebar expand button (the > button) */
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* Custom sidebar width */
    section[data-testid="stSidebar"] {
        width: 300px !important;
    }
    
    section[data-testid="stSidebar"] > div {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .route-badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .route-llm {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
    }
    .route-rag {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    .route-web {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
    }
    .stats-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state with enhanced tracking
def init_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = ChatMessageHistory()
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = []
    if "route_stats" not in st.session_state:
        st.session_state.route_stats = {"llm": 0, "rag": 0, "web": 0}
    if "total_queries" not in st.session_state:
        st.session_state.total_queries = 0
    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.now()

init_session_state()

class EnhancedRouter:
    """Enhanced query router with comprehensive logic for all scenarios"""
    
    def __init__(self, llm):
        self.llm = llm
        self.search_tool = DuckDuckGoSearchRun()
        logger.info("Enhanced router initialized")
        
    def _has_conversation_context(self, query: str, chat_history: List) -> bool:
        """Detect if query refers to previous conversation"""
        if len(chat_history) == 0:
            return False
        
        context_indicators = [
            " it ", " its ", " that ", " this ", " these ", " those ",
            " them ", " they ", " their ",
            "the result", "the answer", "your response", "you said",
            "above", "previous", "earlier", "before",
            "also", "and", "then", "next", "now", "after that",
            "add to", "subtract from", "multiply by", "divide by",
            "plus", "minus", "times"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in context_indicators)
    
    def _is_mathematical(self, query: str) -> bool:
        """Detect mathematical queries comprehensively"""
        query_lower = query.lower()
        has_operators = any(op in query for op in ['+', '-', '*', '/', '=', '^'])
        
        math_keywords = [
            "calculate", "compute", "solve", "evaluate",
            "add", "sum", "plus", "addition",
            "subtract", "minus", "difference",
            "multiply", "times", "product",
            "divide", "quotient",
            "equals", "equal to",
            "square", "power", "root",
            "percentage", "percent"
        ]
        has_math_keywords = any(keyword in query_lower for keyword in math_keywords)
        has_numbers = any(char.isdigit() for char in query)
        
        return has_operators or (has_math_keywords and has_numbers)
    
    def _needs_realtime_data(self, query: str) -> bool:
        """Determine if query genuinely needs real-time web data"""
        query_lower = query.lower()
        
        temporal_words = ["current", "latest", "today", "now", "recent", 
                         "this week", "this month", "right now", "live"]
        
        realtime_data_types = [
            "price", "rate", "stock", "market", "exchange", "crypto", "bitcoin",
            "trading", "value", "worth",
            "news", "breaking", "update", "happening", "event",
            "weather", "temperature", "forecast", "climate",
            "score", "game", "match", "tournament",
            "traffic", "status", "available", "open", "closed"
        ]
        
        has_temporal = any(word in query_lower for word in temporal_words)
        has_realtime_type = any(dtype in query_lower for dtype in realtime_data_types)
        
        return has_temporal and has_realtime_type
    
    def _references_documents(self, query: str, has_documents: bool) -> bool:
        """Detect if query is about uploaded documents"""
        if not has_documents:
            return False
        
        query_lower = query.lower()
        doc_keywords = [
            "document", "file", "pdf", "text", "paper", "article",
            "uploaded", "attachment",
            "in the", "from the", "according to",
            "what does", "summarize", "extract",
            "content", "written", "mentioned"
        ]
        
        return any(keyword in query_lower for keyword in doc_keywords)
        
    def route_query(self, query: str, has_documents: bool, chat_history: List) -> Dict[str, Any]:
        """
        Enhanced routing with confidence scoring
        
        Returns: Dict with 'route', 'confidence', and 'reason'
        """
        try:
            query_lower = query.lower()
            
            # STAGE 1: Simple conversational queries
            simple_phrases = [
                "hello", "hi ", "hey ", "good morning", "good afternoon",
                "good evening", "thanks", "thank you", "bye", "goodbye",
                "how are you", "what's up"
            ]
            if any(query_lower.startswith(phrase) for phrase in simple_phrases):
                return {"route": "llm", "confidence": 1.0, "reason": "Conversational"}
            
            # STAGE 2: Conversation context reference (HIGHEST PRIORITY)
            if self._has_conversation_context(query, chat_history):
                return {"route": "llm", "confidence": 1.0, "reason": "Context reference"}
            
            # STAGE 3: Mathematical queries
            if self._is_mathematical(query):
                return {"route": "llm", "confidence": 1.0, "reason": "Mathematical"}
            
            # STAGE 4: Document queries
            if self._references_documents(query, has_documents):
                return {"route": "rag", "confidence": 0.95, "reason": "Document reference"}
            
            # STAGE 5: Real-time data queries
            if self._needs_realtime_data(query):
                return {"route": "web", "confidence": 0.95, "reason": "Real-time data"}
            
            # STAGE 6: Common LLM query types
            llm_indicators = [
                "explain", "how does", "why", "what is", "who is",
                "describe", "tell me about", "can you",
                "help me", "write", "create", "generate",
                "compare", "difference between"
            ]
            if any(indicator in query_lower for indicator in llm_indicators):
                return {"route": "llm", "confidence": 0.9, "reason": "General knowledge"}
            
            # STAGE 7: DEFAULT - LLM for safety
            return {"route": "llm", "confidence": 0.8, "reason": "Default"}
            
        except Exception as e:
            logger.error(f"Routing error: {str(e)}")
            return {"route": "llm", "confidence": 0.5, "reason": "Error fallback"}

class EnhancedChatbotManager:
    """Enhanced chatbot manager with better error handling"""
    
    def __init__(self, api_key: str):
        try:
            self.llm = ChatGroq(
                temperature=0.7,
                model_name="llama-3.1-8b-instant",  # Faster model
                groq_api_key=api_key,
                max_tokens=2048
            )
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            self.router = EnhancedRouter(self.llm)
            self.search_tool = DuckDuckGoSearchRun()
            logger.info("Chatbot manager initialized successfully")
        except Exception as e:
            logger.error(f"Initialization error: {str(e)}")
            raise
        
    def process_documents(self, uploaded_files) -> Optional[FAISS]:
        """Enhanced document processing with error handling"""
        documents = []
        errors = []
        
        for uploaded_file in uploaded_files:
            try:
                with tempfile.NamedTemporaryFile(delete=False, 
                                                suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Load based on file type
                file_ext = uploaded_file.name.split('.')[-1].lower()
                if file_ext == 'pdf':
                    loader = PyPDFLoader(tmp_path)
                elif file_ext == 'txt':
                    loader = TextLoader(tmp_path)
                elif file_ext == 'docx':
                    loader = Docx2txtLoader(tmp_path)
                else:
                    errors.append(f"Unsupported file type: {uploaded_file.name}")
                    continue
                
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Successfully processed: {uploaded_file.name}")
                
            except Exception as e:
                error_msg = f"Error processing {uploaded_file.name}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
            finally:
                if 'tmp_path' in locals():
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
        
        if errors:
            st.warning("Some files had errors:\n" + "\n".join(errors))
        
        if not documents:
            return None
        
        # Split and create vector store
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        splits = text_splitter.split_documents(documents)
        
        vectorstore = FAISS.from_documents(splits, self.embeddings)
        logger.info(f"Created vector store with {len(splits)} chunks")
        return vectorstore
    
    def answer_with_llm(self, query: str, chat_history: List) -> str:
        """Enhanced LLM answering with intelligent context management"""
        try:
            messages = st.session_state.chat_history.messages
            
            # Build comprehensive context
            context_history = []
            for msg in messages[-12:]:  # Last 6 exchanges
                if isinstance(msg, HumanMessage):
                    context_history.append(f"User: {msg.content}")
                elif isinstance(msg, AIMessage):
                    context_history.append(f"Assistant: {msg.content}")
            
            # Create adaptive prompt
            if context_history:
                context_text = "\n".join(context_history)
                prompt = f"""You are an intelligent AI assistant in an ongoing conversation. Your job is to:
1. Understand and use the conversation history when the user references it
2. Provide accurate calculations and reasoning
3. Maintain conversational flow and context awareness
4. Give direct, precise answers

CONVERSATION HISTORY:
{context_text}

CURRENT USER QUESTION: {query}

CRITICAL INSTRUCTIONS:
- If the user uses words like "it", "that", "this", "the result", or refers to something from history, USE THE CONVERSATION HISTORY ABOVE
- For mathematical operations, show clear step-by-step reasoning
- If continuing a previous topic, acknowledge the connection
- Be natural and conversational while being accurate
- Answer directly without unnecessary preamble

YOUR RESPONSE:"""
            else:
                prompt = f"""You are an intelligent AI assistant. Provide a clear, accurate, and helpful response to the user's question.

USER QUESTION: {query}

INSTRUCTIONS:
- Be accurate and precise
- For math, show your reasoning
- Be conversational and friendly
- Answer directly

YOUR RESPONSE:"""

            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def answer_with_rag(self, query: str, vectorstore: FAISS, chat_history: List) -> str:
        """Answer using RAG with simplified approach"""
        try:
            if vectorstore is None:
                return "No documents available. Please upload documents first."
            
            # Retrieve relevant documents using invoke
            retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
            docs = retriever.invoke(query)  # Updated method
            
            # Build context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt with context
            prompt = f"""You are a helpful AI assistant. Use the following context from documents to answer the question.
If the answer is not in the context, say so clearly.

Context from documents:
{context}

Question: {query}

Answer based on the context above:"""

            # Get answer from LLM
            response = self.llm.invoke(prompt)
            answer = response.content
            
            # Add sources
            if docs:
                answer += "\n\n📚 **Sources:**\n"
                seen_sources = set()
                for i, doc in enumerate(docs[:3], 1):
                    source = os.path.basename(doc.metadata.get("source", "Unknown"))
                    if source not in seen_sources:
                        answer += f"   {i}. {source}\n"
                        seen_sources.add(source)
            
            return answer
            
        except Exception as e:
            logger.error(f"RAG error: {str(e)}")
            return f"Error accessing documents: {str(e)}"
    
    def answer_with_web(self, query: str) -> str:
        """Enhanced web search with fallback"""
        try:
            search_results = self.search_tool.run(query)
            
            synthesis_prompt = f"""Synthesize a comprehensive answer from these web search results.

Query: {query}

Search Results:
{search_results}

Provide a clear, well-structured answer with key information:"""

            response = self.llm.invoke(synthesis_prompt)
            return response.content + "\n\n🌐 *Information from web search*"
            
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            # Fallback to LLM
            return self.answer_with_llm(
                query + " (Note: Web search unavailable, using general knowledge)",
                st.session_state.chat_history.messages
            )
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Enhanced query processing with tracking"""
        try:
            # Route query
            has_documents = st.session_state.vectorstore is not None
            chat_history = st.session_state.chat_history.messages
            
            route_info = self.router.route_query(query, has_documents, chat_history)
            route = route_info["route"]
            
            # Get answer
            if route == "rag":
                answer = self.answer_with_rag(query, st.session_state.vectorstore, chat_history)
            elif route == "web":
                answer = self.answer_with_web(query)
            else:
                answer = self.answer_with_llm(query, chat_history)
            
            # Update memory and stats
            st.session_state.chat_history.add_user_message(query)
            st.session_state.chat_history.add_ai_message(answer)
            st.session_state.route_stats[route] += 1
            st.session_state.total_queries += 1
            
            return {
                "answer": answer,
                "route": route,
                "confidence": route_info.get("confidence", 0),
                "reason": route_info.get("reason", "")
            }
        except Exception as e:
            logger.error(f"Query processing error: {str(e)}")
            return {
                "answer": f"An error occurred: {str(e)}",
                "route": "error",
                "confidence": 0,
                "reason": "Error"
            }

def display_stats():
    """Display session statistics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value">{st.session_state.total_queries}</div>
            <div class="metric-label">Total Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value" style="color: #4caf50;">{st.session_state.route_stats['llm']}</div>
            <div class="metric-label">🟢 LLM</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value" style="color: #2196f3;">{st.session_state.route_stats['rag']}</div>
            <div class="metric-label">🔵 RAG</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="metric-value" style="color: #ff9800;">{st.session_state.route_stats['web']}</div>
            <div class="metric-label">🟠 WEB</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Enhanced main function"""
    st.title("🤖 AI Chatbot Pro")
    st.markdown("**Powered by LLM + RAG + Web Search with Intelligent Routing**")
    
    # Display stats
    display_stats()
    
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Get your free key at https://console.groq.com/keys"
        )
        
        if not api_key:
            st.warning("⚠️ Enter your Groq API key to start")
            st.info("🔑 Get free API key: https://console.groq.com/keys")
            st.stop()
        
        st.divider()
        
        # Document management
        st.header("📄 Documents")
        uploaded_files = st.file_uploader(
            "Upload files",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("🔄 Process Documents", use_container_width=True):
                with st.spinner("Processing..."):
                    chatbot = EnhancedChatbotManager(api_key)
                    st.session_state.vectorstore = chatbot.process_documents(uploaded_files)
                    st.session_state.processed_files = [f.name for f in uploaded_files]
                    st.success(f"✅ Processed {len(uploaded_files)} file(s)")
                    st.rerun()
        
        if st.session_state.processed_files:
            st.success(f"📚 {len(st.session_state.processed_files)} document(s) loaded")
            with st.expander("View files"):
                for f in st.session_state.processed_files:
                    st.text(f"• {f}")
        
        st.divider()
        
        # Session management
        st.header("🔧 Session")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = ChatMessageHistory()
            st.rerun()
        
        if st.button("📊 Reset Stats", use_container_width=True):
            st.session_state.route_stats = {"llm": 0, "rag": 0, "web": 0}
            st.session_state.total_queries = 0
            st.rerun()
        
        st.divider()
        
        with st.expander("ℹ️ Routing Guide"):
            st.markdown("""
            **🟢 LLM**: Conversations, explanations
            **🔵 RAG**: Document questions
            **🟠 WEB**: Current information
            """)
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("route"):
                route_emoji = {"llm": "🟢", "rag": "🔵", "web": "🟠"}
                st.caption(f"{route_emoji.get(message['route'], '')} {message['route'].upper()}")
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Processing..."):
                chatbot = EnhancedChatbotManager(api_key)
                result = chatbot.process_query(prompt)
                
                route_emoji = {"llm": "🟢", "rag": "🔵", "web": "🟠"}
                st.caption(f"{route_emoji.get(result['route'], '')} {result['route'].upper()}")
                st.markdown(result["answer"])
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "route": result["route"]
        })
        
        st.rerun()

if __name__ == "__main__":
    main()
