from ingest import get_vectorstore

def run_test():
    store = get_vectorstore()
    query = "What is the return window for phones?"
    print(f"Searching for: '{query}'\n" + "="*50)
    
    results = store.similarity_search_with_score(query, k=3)
    
    for doc, score in results:
        source = doc.metadata.get("source_file", "Unknown")
        # Lower distance score indicates closer similarity in Chroma vector spaces
        print(f"[{source}] Distance Score: {score:.4f}")
        print(doc.page_content)
        print("-" * 50)

if __name__ == "__main__":
    run_test()