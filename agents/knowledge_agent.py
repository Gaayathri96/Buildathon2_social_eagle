import os
from autogen import ConversableAgent

def search_kb(query: str, category: str = "") -> str:
    """Searches through ShopEase markdown knowledge base files for relevant passages."""
    kb_dir = "knowledge_base"
    if not os.path.exists(kb_dir):
        return "Knowledge base directory not found."
    
    files = [
        "shipping_policy.md",
        "refund_policy.md",
        "account_and_login.md",
        "product_faq.md"
    ]
    
    results = []
    query_lower = query.lower()
    
    for filename in files:
        filepath = os.path.join(kb_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if any(term in content.lower() for term in query_lower.split()) or category.lower() in filename.lower():
                    results.append(f"--- Source: {filename} ---\n{content}\n")
                    
    if not results:
        return "No direct matching document found in the knowledge base."
    
    return "\n".join(results)

def create_knowledge_agent(llm_config):
    agent = ConversableAgent(
        name="KnowledgeBaseAgent",
        system_message="""You are a knowledge retrieval assistant. 
Given the customer issue summary and category, use the `search_kb` tool to search the company markdown documents and pull out only the relevant passages with their source file names.""",
        llm_config=llm_config,
        human_input_mode="NEVER"
    )
    agent.register_for_llm(name="search_kb", description="Search company policy and FAQ documents.")(search_kb)
    return agent, search_kb