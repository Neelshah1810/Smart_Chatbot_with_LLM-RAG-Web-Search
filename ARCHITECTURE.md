# 🏗️ System Architecture

## Overview

This document explains the architecture and data flow of the AI Chatbot with intelligent routing.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                       │
│                      (Streamlit App)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    CHATBOT MANAGER                           │
│  • Orchestrates all components                              │
│  • Manages session state                                    │
│  • Handles errors                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  INTELLIGENT ROUTER                          │
│  • Analyzes user query                                      │
│  • Considers context and history                            │
│  • Selects optimal route                                    │
└────────┬───────────────────────┬──────────────┬─────────────┘
         │                       │              │
    ┌────▼────┐           ┌─────▼─────┐   ┌───▼────┐
    │   LLM   │           │    RAG    │   │  WEB   │
    │  Route  │           │   Route   │   │ Route  │
    └────┬────┘           └─────┬─────┘   └───┬────┘
         │                      │              │
         │                      │              │
         └──────────────────────┴──────────────┘
                                │
                                ▼
                         ┌─────────────┐
                         │  RESPONSE   │
                         │  + Route    │
                         │  Indicator  │
                         └─────────────┘
```

## Component Details

### 1. User Interface Layer (Streamlit)

**Responsibilities:**
- Display chat interface
- Handle file uploads
- Show conversation history
- Display route indicators
- Manage API key input

**Key Features:**
- Responsive design
- Real-time updates
- File management
- Session statistics

### 2. Chatbot Manager

**Responsibilities:**
- Initialize all components (LLM, Embeddings, Router)
- Process user queries
- Manage conversation memory
- Handle document processing
- Coordinate between routes

**Key Methods:**
```python
process_query()         # Main entry point
process_documents()     # Document ingestion
answer_with_llm()      # Direct LLM response
answer_with_rag()      # RAG response
answer_with_web()      # Web search response
```

### 3. Intelligent Router

**Responsibilities:**
- Analyze query content
- Consider available resources
- Review conversation context
- Make routing decision
- Provide confidence scores

**Decision Factors:**
- Query keywords
- Document availability
- Time sensitivity
- Conversation context
- Pattern matching

### 4. LLM Route

**Components:**
- Groq LLM (Llama 3.1 70B)
- Conversation memory
- Context builder

**Use Cases:**
- General conversation
- Explanations
- Creative content
- Analysis and reasoning

**Flow:**
```
User Query → Build Context → LLM → Response
              (History)
```

### 5. RAG Route

**Components:**
- Document Loaders (PDF, TXT, DOCX)
- Text Splitter
- Embeddings Model
- FAISS Vector Store
- Retrieval Chain

**Use Cases:**
- Document Q&A
- Information extraction
- Summarization
- Multi-document queries

**Flow:**
```
User Query → Vector Search → Retrieve Docs → LLM Synthesis → Response
              (FAISS)         (Top-K)         (Context)
```

### 6. Web Route

**Components:**
- DuckDuckGo Search
- Result Parser
- LLM Synthesizer

**Use Cases:**
- Current events
- Real-time data
- Recent information
- Fact checking

**Flow:**
```
User Query → Web Search → Parse Results → LLM Synthesis → Response
              (DDG)        (Extract)       (Context)
```

## Data Flow Diagram

### Query Processing Flow

```
┌──────────────┐
│  User Query  │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│  Query Analysis     │
│  • Keywords         │
│  • Intent           │
│  • Context          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Route Decision     │
│  LLM / RAG / WEB    │
└──────┬──────────────┘
       │
       ├────────────┬───────────┐
       │            │           │
       ▼            ▼           ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│   LLM    │  │   RAG    │  │   WEB    │
│ Generate │  │ Retrieve │  │  Search  │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │            │              │
     └────────────┴──────────────┘
                  │
                  ▼
         ┌────────────────┐
         │   Response     │
         │   + Metadata   │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │   Update       │
         │   Memory       │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │   Display      │
         │   to User      │
         └────────────────┘
```

## Document Processing Pipeline

```
┌─────────────────┐
│  Upload Files   │
│  (PDF/TXT/DOCX) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Load Documents │
│  • PyPDF       │
│  • TextLoader  │
│  • Docx2txt    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Split Text     │
│  • Chunk: 1000  │
│  • Overlap: 200 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate       │
│  Embeddings     │
│  (HuggingFace)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create Vector  │
│  Store (FAISS)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ready for      │
│  Queries        │
└─────────────────┘
```

## Routing Decision Tree

```
                    User Query
                        │
                        ▼
              ┌─────────────────┐
              │ Is Greeting?    │
              └────┬───────┬────┘
                   │Yes    │No
                   │       │
                   ▼       ▼
                 LLM   ┌──────────────┐
                       │ Has Current  │
                       │ Keywords?    │
                       └───┬─────┬────┘
                           │Yes  │No
                           │     │
                           ▼     ▼
                         WEB  ┌──────────────┐
                              │ Documents    │
                              │ Available?   │
                              └───┬─────┬────┘
                                  │Yes  │No
                                  │     │
                                  ▼     ▼
                              ┌──────────┐
                              │ Has Doc  │
                              │ Keywords?│
                              └───┬──┬───┘
                                  │  │
                                Yes│  │No
                                  │  │
                                  ▼  ▼
                                RAG LLM
```

## Memory Management

```
┌────────────────────────────────────┐
│      Conversation Memory            │
├────────────────────────────────────┤
│                                     │
│  ┌──────────────────────────────┐  │
│  │ User: Hello!                 │  │
│  │ Assistant: Hi! How are you?  │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ User: What's 2+2?           │  │
│  │ Assistant: 4                 │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ User: [Current Query]       │  │
│  │ Assistant: [Response]        │  │
│  └──────────────────────────────┘  │
│                                     │
└────────────────────────────────────┘
         │
         ▼
Used for Context in Next Query
```

## Session State Management

```
Session State (st.session_state)
├── messages[]           # Chat history
├── vectorstore         # Document embeddings
├── memory             # Conversation memory
├── processed_files[]  # Uploaded file names
├── route_stats{}      # Route usage counts
└── total_queries      # Query counter
```

## Error Handling Flow

```
┌──────────────┐
│   Try Query  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Success?   │
└───┬──────┬───┘
    │Yes   │No
    │      │
    ▼      ▼
Response  ┌────────────┐
          │  Log Error │
          └──────┬─────┘
                 │
                 ▼
          ┌────────────┐
          │  Fallback  │
          │  to LLM?   │
          └───┬────┬───┘
              │Yes │No
              │    │
              ▼    ▼
           LLM   Error
         Response Message
```

## Performance Optimizations

### 1. Caching
- Embeddings model cached in session
- Vector store persists during session
- LLM client reused

### 2. Lazy Loading
- Documents loaded on demand
- Embeddings generated once

### 3. Efficient Retrieval
- Top-K search (K=4)
- FAISS for fast similarity search

### 4. Memory Management
- Buffer-based conversation memory
- Automatic truncation for long chats

## Security Considerations

### 1. API Key Handling
- Stored in session state only
- Never logged or displayed
- User-provided (not hardcoded)

### 2. File Upload Safety
- Type validation
- Size limits
- Temporary file cleanup

### 3. Error Messages
- Sanitized for production
- Detailed logging for debugging

## Scalability

### Current Limitations
- In-memory vector store
- Single-user sessions
- No persistent storage

### Potential Improvements
- Database-backed vector store
- Shared document collections
- User authentication
- Query caching

## Technology Stack Details

### Core Framework
- **LangChain**: Orchestration
- **Streamlit**: UI Framework

### Models
- **LLM**: Groq (Llama 3.1 70B)
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)

### Vector Store
- **FAISS**: Fast similarity search

### Search
- **DuckDuckGo**: Web search API

### Document Processing
- **PyPDF**: PDF parsing
- **python-docx**: DOCX parsing
- **TextLoader**: Plain text

## Deployment Architecture

```
┌─────────────────────────────────────┐
│         Local Development           │
├─────────────────────────────────────┤
│  • streamlit run chatbot_app.py     │
│  • localhost:8501                   │
│  • Hot reload enabled               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│         Cloud Deployment            │
├─────────────────────────────────────┤
│  • Streamlit Cloud                  │
│  • Heroku                           │
│  • AWS/GCP/Azure                    │
│  • Docker container                 │
└─────────────────────────────────────┘
```

## Monitoring & Logging

### Logged Events
- Query routing decisions
- Document processing status
- Error occurrences
- API call failures

### Metrics (Enhanced Version)
- Total queries
- Route distribution
- Session duration
- Error rate

---

This architecture provides a robust, scalable foundation for an intelligent chatbot with multi-source information retrieval capabilities.
