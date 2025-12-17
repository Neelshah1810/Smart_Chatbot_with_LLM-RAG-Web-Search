"""
Test script to demonstrate the intelligent routing logic
Run this after setting up your environment to see how routing works
"""

def demonstrate_routing():
    """Show examples of how queries get routed"""
    
    print("=" * 70)
    print("INTELLIGENT QUERY ROUTING DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Example queries with expected routes
    test_cases = [
        # LLM Route Examples
        ("Hello, how are you?", "LLM", "Conversational greeting"),
        ("Explain quantum computing", "LLM", "General knowledge question"),
        ("Write a poem about AI", "LLM", "Creative task"),
        ("What is 2 + 2?", "LLM", "Simple calculation"),
        
        # RAG Route Examples (when documents are available)
        ("What does the document say about climate change?", "RAG", "Direct document reference"),
        ("Summarize the uploaded PDF", "RAG", "Document summarization"),
        ("According to the file, what is the conclusion?", "RAG", "File-specific query"),
        ("What are the key points in the text?", "RAG", "Content extraction"),
        
        # WEB Route Examples
        ("What's the latest news about AI?", "WEB", "Current news request"),
        ("What's the weather today?", "WEB", "Real-time data"),
        ("Current stock price of Tesla", "WEB", "Up-to-date information"),
        ("Who won the 2024 election?", "WEB", "Recent event"),
        ("What happened in the news today?", "WEB", "Today's events"),
    ]
    
    print("📊 ROUTING EXAMPLES:\n")
    
    for query, expected_route, description in test_cases:
        route_emoji = {
            "LLM": "🟢",
            "RAG": "🔵",
            "WEB": "🟠"
        }
        
        print(f"{route_emoji[expected_route]} {expected_route} Route")
        print(f"   Query: \"{query}\"")
        print(f"   Reason: {description}")
        print()
    
    print("=" * 70)
    print("\nKEY ROUTING RULES:")
    print("=" * 70)
    print()
    
    print("🟢 LLM Route (Direct Response):")
    print("   - Conversational queries (greetings, thanks)")
    print("   - General knowledge and explanations")
    print("   - Creative content generation")
    print("   - Analysis and reasoning tasks")
    print("   - Questions that don't need real-time data or documents")
    print()
    
    print("🔵 RAG Route (Document Search):")
    print("   - Keywords: 'document', 'file', 'pdf', 'uploaded', 'text'")
    print("   - Phrases: 'according to', 'in the document', 'from the file'")
    print("   - Requires documents to be uploaded first")
    print("   - Searches through vector database of documents")
    print()
    
    print("🟠 WEB Route (Internet Search):")
    print("   - Keywords: 'latest', 'current', 'today', 'now', 'recent', 'news'")
    print("   - Real-time data requests (weather, stocks, scores)")
    print("   - Current events and breaking news")
    print("   - Information that changes frequently")
    print()
    
    print("=" * 70)
    print("\nROUTING LOGIC FLOW:")
    print("=" * 70)
    print("""
    1. User submits query
    2. LLM analyzes query context
    3. System checks for routing keywords
    4. Override rules apply (if needed)
    5. Final route determination
    6. Query processed through selected route
    7. Response returned with route indicator
    """)
    
    print("=" * 70)
    print("\nADVANCED FEATURES:")
    print("=" * 70)
    print()
    print("✅ Context-Aware: Uses conversation history for better routing")
    print("✅ Fallback System: If web search fails, falls back to LLM")
    print("✅ Multi-Criteria: Combines LLM decision + keyword matching")
    print("✅ Override Logic: Hard rules for certain query patterns")
    print("✅ Confidence Scoring: Validates routing decisions")
    print()
    
    print("=" * 70)
    print("\n💡 TIPS FOR BEST RESULTS:")
    print("=" * 70)
    print()
    print("1. Be explicit when asking about documents:")
    print("   ✅ \"What does the uploaded document say about...\"")
    print("   ❌ \"Tell me about...\" (might route to LLM)")
    print()
    print("2. Use time-based keywords for current info:")
    print("   ✅ \"What's the latest news about...\"")
    print("   ✅ \"Current price of...\"")
    print()
    print("3. For general knowledge, keep queries simple:")
    print("   ✅ \"Explain quantum physics\"")
    print("   ✅ \"How does photosynthesis work?\"")
    print()
    
    print("=" * 70)
    print("Ready to try the chatbot? Run: streamlit run chatbot_app.py")
    print("=" * 70)

if __name__ == "__main__":
    demonstrate_routing()
