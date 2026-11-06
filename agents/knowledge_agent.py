import os
import chromadb
from autogen import ConversableAgent

def get_vector_collection():
    """Initializes ChromaDB persistent client and indexes markdown KB docs if empty."""
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection(name="shopease_kb")
    
    if collection.count() == 0:
        kb_dir = "knowledge_base"
        if os.path.exists(kb_dir):
            for filename in os.listdir(kb_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(kb_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        collection.add(
                            documents=[content],
                            metadatas=[{"source": filename}],
                            ids=[filename]
                        )
    return collection

def search_kb_vector(query: str) -> str:
    """Semantic vector search over ShopEase markdown policies using ChromaDB."""
    try:
        collection = get_vector_collection()
        results = collection.query(query_texts=[query], n_results=2)
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        
        if not docs:
            return "No matching document found in vector store."
        
        formatted = []
        for doc, meta in zip(docs, metas):
            source = meta.get("source", "Unknown")
            formatted.append(f"--- Source: {source} ---\n{doc}\n")
        return "\n".join(formatted)
    except Exception as e:
        return f"Vector search error: {str(e)}"

def create_knowledge_agent(llm_config):
    agent = ConversableAgent(
        name="KnowledgeBaseAgent",
        system_message="You are a knowledge retrieval assistant. Use the `search_kb_vector` tool to retrieve semantically relevant policy passages and source files for customer inquiries.",
        llm_config=llm_config,
        human_input_mode="NEVER"
    )
    agent.register_for_llm(name="search_kb_vector", description="Semantic vector search for company policies and FAQs.")(search_kb_vector)
    return agent, search_kb_vector