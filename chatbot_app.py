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
from typing import List, Dict, Any
import json

# Page configuration
st.set_page_config(
    page_title="AI Chatbot with RAG & Web Search",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

# Custom CSS for better UI
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
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .route-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .route-llm {
        background-color: #4caf50;
        color: white;
    }
    .route-rag {
        background-color: #2196f3;
        color: white;
    }
    .route-web {
        background-color: #ff9800;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class IntelligentRouter:
    """Advanced query router with comprehensive logic for all scenarios"""
    
    def __init__(self, llm):
        self.llm = llm
        self.search_tool = DuckDuckGoSearchRun()
        
    def _has_conversation_context(self, query: str, chat_history: List) -> bool:
        """Detect if query refers to previous conversation"""
        if len(chat_history) == 0:
            return False
        
        # Pronouns and references that indicate continuation
        context_indicators = [
            # Pronouns
            " it ", " its ", " that ", " this ", " these ", " those ",
            " them ", " they ", " their ",
            # Direct references
            "the result", "the answer", "your response", "you said",
            "above", "previous", "earlier", "before",
            # Action continuations
            "also", "and", "then", "next", "now", "after that",
            # Math continuations
            "add to", "subtract from", "multiply by", "divide by",
            "plus", "minus", "times"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in context_indicators)
    
    def _is_mathematical(self, query: str) -> bool:
        """Detect mathematical queries comprehensively"""
        query_lower = query.lower()
        
        # Math operators
        has_operators = any(op in query for op in ['+', '-', '*', '/', '=', '^'])
        
        # Math keywords
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
        
        # Has numbers
        has_numbers = any(char.isdigit() for char in query)
        
        # Mathematical if has operators OR (has keywords AND numbers)
        return has_operators or (has_math_keywords and has_numbers)
    
    def _needs_realtime_data(self, query: str) -> bool:
        """Determine if query genuinely needs real-time web data"""
        query_lower = query.lower()
        
        # Temporal indicators (must be combined with data requests)
        temporal_words = ["current", "latest", "today", "now", "recent", 
                         "this week", "this month", "right now", "live"]
        
        # Types of data that change frequently
        realtime_data_types = [
            # Financial
            "price", "rate", "stock", "market", "exchange", "crypto", "bitcoin",
            "trading", "value", "worth",
            # News & Events  
            "news", "breaking", "update", "happening", "event",
            # Weather
            "weather", "temperature", "forecast", "climate",
            # Sports
            "score", "game", "match", "tournament",
            # Other real-time
            "traffic", "status", "available", "open", "closed"
        ]
        
        has_temporal = any(word in query_lower for word in temporal_words)
        has_realtime_type = any(dtype in query_lower for dtype in realtime_data_types)
        
        # Needs web if asking for temporal + realtime data type
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
    
    def route_query(self, query: str, has_documents: bool, chat_history: List) -> str:
        """
        Intelligently route query using comprehensive analysis
        
        Returns: 'llm', 'rag', or 'web'
        """
        query_lower = query.lower()
        
        # STAGE 1: Simple conversational queries
        simple_phrases = [
            "hello", "hi ", "hey ", "good morning", "good afternoon",
            "good evening", "thanks", "thank you", "bye", "goodbye",
            "how are you", "what's up", "sup", "yo "
        ]
        if any(query_lower.startswith(phrase) for phrase in simple_phrases):
            return "llm"
        
        # STAGE 2: Check for conversation context reference
        # If referring to previous messages, ALWAYS use LLM to maintain context
        if self._has_conversation_context(query, chat_history):
            return "llm"
        
        # STAGE 3: Mathematical queries
        # Math should be handled by LLM, not web search
        if self._is_mathematical(query):
            return "llm"
        
        # STAGE 4: Document queries
        # If asking about uploaded documents
        if self._references_documents(query, has_documents):
            return "rag"
        
        # STAGE 5: Real-time data queries
        # Only route to web if TRULY needs current data
        if self._needs_realtime_data(query):
            return "web"
        
        # STAGE 6: Specific question types that should use LLM
        llm_indicators = [
            "explain", "how does", "why", "what is", "who is",
            "describe", "tell me about", "can you",
            "help me", "i need", "i want",
            "write", "create", "generate", "make",
            "compare", "difference between"
        ]
        if any(indicator in query_lower for indicator in llm_indicators):
            return "llm"
        
        # STAGE 7: DEFAULT - Use LLM for general queries
        # LLM is the safest default as it handles most cases well
        return "llm"

class ChatbotManager:
    """Manages the chatbot operations"""
    
    def __init__(self, api_key: str):
        self.llm = ChatGroq(
            temperature=0.7,
            model_name="llama-3.1-8b-instant",  # Faster model
            groq_api_key=api_key
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.router = IntelligentRouter(self.llm)
        self.search_tool = DuckDuckGoSearchRun()
        
    def process_documents(self, uploaded_files) -> FAISS:
        """Process uploaded documents and create vector store"""
        documents = []
        
        for uploaded_file in uploaded_files:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                # Load document based on file type
                if uploaded_file.name.endswith('.pdf'):
                    loader = PyPDFLoader(tmp_path)
                elif uploaded_file.name.endswith('.txt'):
                    loader = TextLoader(tmp_path)
                elif uploaded_file.name.endswith('.docx'):
                    loader = Docx2txtLoader(tmp_path)
                else:
                    st.warning(f"Unsupported file type: {uploaded_file.name}")
                    continue
                
                docs = loader.load()
                documents.extend(docs)
                
            finally:
                # Clean up temp file
                os.unlink(tmp_path)
        
        if not documents:
            return None
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        splits = text_splitter.split_documents(documents)
        
        # Create vector store
        vectorstore = FAISS.from_documents(splits, self.embeddings)
        return vectorstore
    
    def answer_with_llm(self, query: str, chat_history: List) -> str:
        """Answer using LLM with intelligent context management"""
        messages = st.session_state.chat_history.messages
        
        # Build comprehensive context
        context_history = []
        for msg in messages[-12:]:  # Last 6 exchanges for full context
            if isinstance(msg, HumanMessage):
                context_history.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                context_history.append(f"Assistant: {msg.content}")
        
        # Create adaptive prompt based on context availability
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
            # No history - first interaction
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
    
    def answer_with_rag(self, query: str, vectorstore: FAISS, chat_history: List) -> str:
        """Answer using RAG on uploaded documents - Simplified approach"""
        try:
            if vectorstore is None:
                return "No documents have been uploaded yet. Please upload documents to use RAG."
            
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
                answer += "\n\n**Sources:**\n"
                seen_sources = set()
                for i, doc in enumerate(docs[:3], 1):
                    source = os.path.basename(doc.metadata.get("source", "Unknown"))
                    if source not in seen_sources:
                        answer += f"{i}. {source}\n"
                        seen_sources.add(source)
            
            return answer
            
        except Exception as e:
            return f"Error accessing documents: {str(e)}"
    
    def answer_with_web(self, query: str) -> str:
        """Answer using web search"""
        try:
            # Perform web search
            search_results = self.search_tool.run(query)
            
            # Use LLM to synthesize the search results
            synthesis_prompt = f"""Based on the following web search results, provide a comprehensive and accurate answer to the user's query.

User Query: {query}

Search Results:
{search_results}

Instructions:
- Synthesize the information into a clear, coherent answer
- Include relevant facts and details
- If the search results don't contain enough information, say so
- Be concise but informative

Answer:"""

            response = self.llm.invoke(synthesis_prompt)
            return response.content + "\n\n*Source: Web Search*"
            
        except Exception as e:
            return f"Web search encountered an error: {str(e)}\nLet me try to answer from my knowledge instead.\n\n" + self.answer_with_llm(query, st.session_state.chat_history.messages)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Main query processing with intelligent routing"""
        # Determine route
        has_documents = st.session_state.vectorstore is not None
        chat_history = st.session_state.chat_history.messages
        
        route = self.router.route_query(query, has_documents, chat_history)
        
        # Get answer based on route
        if route == "rag":
            answer = self.answer_with_rag(query, st.session_state.vectorstore, chat_history)
        elif route == "web":
            answer = self.answer_with_web(query)
        else:  # llm
            answer = self.answer_with_llm(query, chat_history)
        
        # Update memory
        st.session_state.chat_history.add_user_message(query)
        st.session_state.chat_history.add_ai_message(answer)
        
        return {
            "answer": answer,
            "route": route
        }

# Main UI
def main():
    st.title("🤖 Intelligent AI Chatbot")
    st.markdown("**LLM + RAG + Web Search with Smart Query Routing**")
    
    # Sidebar for configuration and file upload
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Enter your Groq API key to enable the chatbot"
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your Groq API key to continue")
            st.info("Get your free API key at: https://console.groq.com/keys")
            st.stop()
        
        st.divider()
        
        # File upload section
        st.header("📄 Document Upload")
        uploaded_files = st.file_uploader(
            "Upload documents for RAG",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            help="Upload PDF, TXT, or DOCX files"
        )
        
        if uploaded_files:
            if st.button("🔄 Process Documents", use_container_width=True):
                with st.spinner("Processing documents..."):
                    chatbot = ChatbotManager(api_key)
                    st.session_state.vectorstore = chatbot.process_documents(uploaded_files)
                    st.session_state.processed_files = [f.name for f in uploaded_files]
                    st.success(f"✅ Processed {len(uploaded_files)} document(s)")
        
        if st.session_state.processed_files:
            st.info(f"📚 Active documents:\n" + "\n".join([f"- {f}" for f in st.session_state.processed_files]))
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = ChatMessageHistory()
            st.rerun()
        
        st.divider()
        
        # Routing information
        with st.expander("ℹ️ How Routing Works"):
            st.markdown("""
            **🟢 LLM Route**: General conversation, explanations, creative tasks
            
            **🔵 RAG Route**: Questions about uploaded documents
            
            **🟠 WEB Route**: Current events, real-time data, latest information
            
            The system automatically chooses the best route for each query!
            """)
    
    # Main chat interface
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        route = message.get("route", "")
        
        with st.chat_message(role):
            if role == "assistant" and route:
                # Display route badge
                route_colors = {
                    "llm": "🟢",
                    "rag": "🔵",
                    "web": "🟠"
                }
                st.caption(f"{route_colors.get(route, '')} Route: {route.upper()}")
            st.markdown(content)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                chatbot = ChatbotManager(api_key)
                result = chatbot.process_query(prompt)
                
                # Display route badge
                route_colors = {
                    "llm": "🟢",
                    "rag": "🔵",
                    "web": "🟠"
                }
                st.caption(f"{route_colors.get(result['route'], '')} Route: {result['route'].upper()}")
                st.markdown(result["answer"])
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["answer"],
            "route": result["route"]
        })
        
        st.rerun()

if __name__ == "__main__":
    main()
