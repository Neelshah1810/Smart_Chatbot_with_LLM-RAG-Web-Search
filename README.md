# 🤖 Intelligent AI Chatbot with LLM + RAG + Web Search

A powerful chatbot application that intelligently routes queries between direct LLM responses, Retrieval-Augmented Generation (RAG) on uploaded documents, and real-time web search.

## ✨ Features

### 🎯 Intelligent Query Routing
- **Automatic Detection**: Uses an LLM-based routing system to automatically determine the best source for each query
- **Multi-Criteria Analysis**: Considers query content, available documents, and conversation history
- **Three Routes**:
  - 🟢 **LLM Route**: General conversation, explanations, reasoning, creative tasks
  - 🔵 **RAG Route**: Questions about uploaded documents and files
  - 🟠 **WEB Route**: Current events, real-time data, latest news

### 📚 Document Processing (RAG)
- Upload multiple documents (PDF, TXT, DOCX)
- Automatic text extraction and chunking
- Semantic search using FAISS vector store
- Source citation for answers from documents
- Supports large documents with efficient retrieval

### 🌐 Web Search Integration
- Real-time web search using DuckDuckGo
- Automatic synthesis of search results
- Perfect for current events and up-to-date information
- Fallback mechanism if search fails

### 💬 Conversation Memory
- Maintains full conversation history
- Context-aware responses
- References previous messages naturally
- Can be cleared at any time

### 🎨 User Interface
- Clean, modern Streamlit interface
- Visual route indicators for each response
- Easy document management
- Responsive design

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Groq API key (free at https://console.groq.com/keys)

### Step 1: Clone or Download
Download the files:
- `chatbot_app.py`
- `requirements.txt`

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run chatbot_app.py
```

The application will open in your default browser at `http://localhost:8501`

## 🔑 Getting Your Groq API Key

1. Visit https://console.groq.com/keys
2. Sign up or log in
3. Create a new API key
4. Copy the key and paste it in the sidebar of the application

**Note**: Groq offers free API access with generous rate limits!

## 📖 Usage Guide

### Basic Conversation
Just type your question and press Enter. The system will automatically route to the LLM for general queries.

**Examples**:
- "Hello, how are you?"
- "Explain quantum computing to me"
- "Write a poem about AI"

### Using RAG with Documents

1. **Upload Documents**:
   - Click "Browse files" in the sidebar
   - Select PDF, TXT, or DOCX files
   - Click "🔄 Process Documents"

2. **Ask Questions About Documents**:
   - "What is the main topic of the document?"
   - "Summarize the key points from the uploaded file"
   - "According to the document, what is..."

### Using Web Search

Ask questions about current information:
- "What's the latest news about AI?"
- "What's the weather today?"
- "Who won the recent election?"
- "Current stock price of Tesla"

## 🎯 How Query Routing Works

The intelligent routing system analyzes each query using multiple factors:

### RAG Route Triggers
- Keywords: "document", "file", "pdf", "uploaded", "in the text"
- Phrases: "according to", "from the", "what does it say"
- When documents are available and query references them

### Web Route Triggers
- Keywords: "latest", "current", "today", "now", "recent", "news"
- Real-time data requests: weather, stock prices, scores
- Date references: "2024", "2025"

### LLM Route (Default)
- General conversation and greetings
- Explanations and reasoning
- Creative content generation
- Analysis and opinions
- When other routes aren't clearly better

## 🏗️ Architecture

```
User Query
    ↓
Query Router (LLM-based)
    ↓
    ├─→ LLM Route ──→ Direct LLM Response
    ├─→ RAG Route ──→ Vector Search + LLM
    └─→ WEB Route ──→ Web Search + LLM Synthesis
    ↓
Response + Route Indicator
```

## 🛠️ Technical Details

### Core Components

1. **ChatbotManager**: Main orchestration class
   - Manages LLM initialization
   - Handles document processing
   - Coordinates routing and responses

2. **IntelligentRouter**: Query routing logic
   - LLM-based route determination
   - Override rules for accuracy
   - Keyword-based enhancements

3. **Document Processing**:
   - RecursiveCharacterTextSplitter (1000 char chunks, 200 overlap)
   - HuggingFace embeddings (all-MiniLM-L6-v2)
   - FAISS vector store for retrieval

4. **Memory System**:
   - ConversationBufferMemory
   - Full conversation history
   - Context-aware responses

### Models Used

- **LLM**: Groq's Llama 3.1 70B (fast and powerful)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Search**: DuckDuckGo Search API

## 📊 Example Interactions

### Example 1: General Conversation
```
User: Hello! How are you today?
Route: 🟢 LLM
Assistant: Hello! I'm doing great, thank you for asking! I'm here and ready to help you with any questions or tasks you have. How can I assist you today?
```

### Example 2: Document Question
```
User: What are the main findings in the uploaded research paper?
Route: 🔵 RAG
Assistant: Based on the research paper, the main findings include:
1. [Extracted finding from document]
2. [Extracted finding from document]
...

Sources:
1. research_paper.pdf
```

### Example 3: Current Information
```
User: What's the latest news in AI?
Route: 🟠 WEB
Assistant: [Synthesized answer from web search results]

*Source: Web Search*
```

## 🔧 Customization

### Adjust Chunk Size
In `ChatbotManager.process_documents()`:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Adjust this
    chunk_overlap=200,  # And this
    length_function=len
)
```

### Change LLM Model
In `ChatbotManager.__init__()`:
```python
self.llm = ChatGroq(
    temperature=0.7,  # Adjust creativity
    model_name="llama-3.1-70b-versatile",  # Change model
    groq_api_key=api_key
)
```

### Modify Routing Logic
Edit the `IntelligentRouter.route_query()` method to add custom routing rules.

## 🐛 Troubleshooting

### Issue: "No module named 'streamlit'"
**Solution**: Make sure you've installed requirements: `pip install -r requirements.txt`

### Issue: "API key error"
**Solution**: Verify your Groq API key is correct and active

### Issue: "Document processing fails"
**Solution**: Check that your document is not corrupted and is in a supported format (PDF, TXT, DOCX)

### Issue: "Web search not working"
**Solution**: Check your internet connection. If DuckDuckGo is blocked, the system will fallback to LLM responses

## 📝 Best Practices

1. **Document Upload**: Process documents before asking questions about them
2. **Clear Questions**: Be specific in your queries for better routing
3. **Context**: The chatbot remembers conversation history, so you can ask follow-up questions
4. **Web Queries**: Use words like "latest", "current", "today" for web search routing
5. **Document Queries**: Reference "the document" or "uploaded file" explicitly

## 🚧 Limitations

- Free Groq API has rate limits (though very generous)
- Web search depends on DuckDuckGo availability
- Large documents may take time to process
- Vector store is in-memory (resets when app restarts)

## 🔮 Future Enhancements

- Persistent vector store (save processed documents)
- Multiple LLM provider support
- Advanced web scraping capabilities
- Export conversation history
- Custom routing rules via UI
- Image document support
- Multi-language support

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the example interactions
3. Ensure all dependencies are installed correctly

## 🙏 Acknowledgments

- LangChain for the excellent framework
- Groq for fast LLM inference
- Streamlit for the user interface
- HuggingFace for embeddings

---

**Built with ❤️ using LangChain, Groq, and Streamlit**
