# 🚀 AI Chatbot Project - Complete Package

## 📦 What's Included

This package contains a fully functional AI chatbot with intelligent query routing between LLM, RAG, and Web Search capabilities.

### Main Application Files

1. **chatbot_app.py** - Core application (Recommended for most users)
   - Complete chatbot with LLM + RAG + Web Search
   - Intelligent query routing
   - Conversation memory
   - Clean, user-friendly interface

2. **chatbot_app_enhanced.py** - Enhanced version
   - All features from core app
   - Session statistics dashboard
   - Better error handling
   - Performance logging
   - Advanced routing with confidence scores

### Documentation

3. **README.md** - Comprehensive documentation
   - Detailed feature explanations
   - Architecture overview
   - Advanced usage guide
   - Troubleshooting tips

4. **QUICKSTART.md** - Get started in 5 minutes
   - Step-by-step setup
   - Quick examples
   - Common issues

### Configuration & Testing

5. **requirements.txt** - Python dependencies
   - All required packages
   - Version-locked for stability

6. **test_routing.py** - Routing demonstration
   - Shows how queries are routed
   - Example queries for each route
   - Educational tool

7. **config_template.py** - Advanced configuration
   - Customization options
   - Model settings
   - Performance tuning

## 🎯 Key Features

### ✅ Intelligent Query Routing
- **LLM Route** (🟢): For general conversation, explanations, creative tasks
- **RAG Route** (🔵): For questions about uploaded documents
- **WEB Route** (🟠): For current events and real-time information

### ✅ Document Processing (RAG)
- Upload PDF, TXT, DOCX files
- Semantic search with FAISS
- Source citations
- Multi-document support

### ✅ Web Search
- Real-time web search via DuckDuckGo
- Intelligent result synthesis
- Automatic fallback handling

### ✅ Conversation Memory
- Maintains full chat history
- Context-aware responses
- Natural follow-up questions

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get API Key
Visit: https://console.groq.com/keys
Sign up and create a free API key

### 3. Run the App
```bash
streamlit run chatbot_app.py
```

### 4. Start Chatting!
Enter your API key in the sidebar and start asking questions!

## 💡 Usage Examples

### General Chat (LLM Route)
```
"Hello! Tell me about yourself"
"Explain quantum computing"
"Write a creative story"
```

### Document Questions (RAG Route)
1. Upload your documents
2. Click "Process Documents"
3. Ask: "What are the main points in the document?"

### Current Information (WEB Route)
```
"What's the latest AI news?"
"Current weather forecast"
"Recent tech developments"
```

## 🎨 Route Selection Logic

The system intelligently chooses the best route based on:
- Query keywords and phrases
- Availability of documents
- Conversation context
- Time-sensitive indicators

### RAG Route Triggers
- Keywords: "document", "file", "uploaded", "pdf"
- Phrases: "according to", "in the document"

### WEB Route Triggers
- Keywords: "latest", "current", "today", "recent"
- Real-time queries: weather, stocks, news

### LLM Route (Default)
- Conversations and greetings
- General knowledge
- Creative tasks
- Explanations

## 📊 Technical Stack

- **LLM**: Groq (Llama 3.1 70B)
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Vector Store**: FAISS
- **Web Search**: DuckDuckGo
- **Framework**: LangChain
- **UI**: Streamlit

## 🔧 Customization

### Change LLM Model
Edit in chatbot_app.py:
```python
model_name="llama-3.1-70b-versatile"  # Change this
```

### Adjust Document Chunking
```python
chunk_size=1000  # Larger = more context
chunk_overlap=200  # More overlap = better continuity
```

### Modify Routing Keywords
Add your own keywords in the routing logic

## 📁 File Structure

```
chatbot-project/
├── chatbot_app.py              # Main application
├── chatbot_app_enhanced.py     # Enhanced version
├── requirements.txt            # Dependencies
├── README.md                   # Full documentation
├── QUICKSTART.md              # Quick start guide
├── test_routing.py            # Routing demo
└── config_template.py         # Configuration options
```

## 🎓 Best Practices

1. **Upload documents first** before asking about them
2. **Be explicit** in your queries for better routing
3. **Use keywords** like "document", "latest" to guide routing
4. **Clear chat** when switching topics
5. **Process documents** after uploading

## ⚡ Performance Tips

- Keep documents under 10MB each
- Process documents once, query multiple times
- Use specific queries for better RAG results
- Web search is rate-limited, use when needed

## 🐛 Common Issues

### "No module found"
Solution: `pip install -r requirements.txt`

### "API key error"
Solution: Check your Groq API key is valid

### "Document processing fails"
Solution: Ensure file is PDF/TXT/DOCX and not corrupted

### "Web search timeout"
Solution: Check internet connection, system will fallback to LLM

## 🚀 Advanced Features (Enhanced Version)

- Session statistics dashboard
- Query confidence scores
- Performance logging
- Better error messages
- Route analytics

## 📈 Future Enhancements

Potential additions:
- Persistent storage for documents
- Multiple LLM providers
- Image document support
- Export conversations
- Custom routing rules UI
- Voice input/output

## 🤝 Support

For issues or questions:
1. Check README.md for detailed docs
2. Review QUICKSTART.md for setup
3. Run test_routing.py to understand routing
4. Check logs for error details

## 📜 License

Open source - MIT License

## 🙏 Credits

Built with:
- LangChain for the framework
- Groq for fast LLM inference
- Streamlit for the UI
- HuggingFace for embeddings

---

## 🎯 Which Version to Use?

### Use **chatbot_app.py** if you want:
- Simple, clean interface
- Quick setup
- Standard features
- Lightweight application

### Use **chatbot_app_enhanced.py** if you want:
- Statistics dashboard
- Performance monitoring
- Advanced error handling
- Production-ready features

Both versions have identical core functionality - choose based on your needs!

---

**🤖 Ready to build amazing conversational AI? Start with chatbot_app.py and scale up as needed!**

---

## 📞 Getting Help

1. **Read the docs**: README.md has everything
2. **Quick setup**: QUICKSTART.md for fast start
3. **Test routing**: Run test_routing.py
4. **Customize**: Use config_template.py

**Happy building! 🚀**
