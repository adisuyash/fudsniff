from rag_system import RAGManager

def main():
    print("🔧 Setting up RAG system...")

    try:
        rag = RAGManager()
        print("✅ RAG system initialized successfully")

        query = {
            'token_symbol': 'BTC',
            'signal_type': 'BUY',
            'reasoning': 'Massive accumulation around key support',
        }

        results = rag.find_similar_signals(query)
        print(f"🔍 Found {len(results)} similar signals")

        for signal, score in results:
            print(f"- {signal.signal_id} | {signal.token_symbol} | {signal.signal_type} | score: {score:.2f}")

    except Exception as e:
        print(f"❌ RAG system failed: {e}")

if __name__ == "__main__":
    main()
