import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from tools import get_order_status
from policy_search import search_policies

load_dotenv()

SORRY = "Sorry, I can only help with KartEase orders and policies."

SYSTEM_PROMPT = f"""You are KartEase customer support.
- Use the tools to answer. Never guess or use outside knowledge.
- Use get_order_status for order lookups and search_policies for policy questions.
- If a question needs both an order's details and a policy, use both tools.
- For anything unrelated to KartEase orders or policies, reply exactly: {SORRY}
Keep answers short and friendly."""

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)

# Convert plain functions into LangChain tools using @tool/tool decorator
tools = [tool(get_order_status), tool(search_policies)]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)


def ask(agent, question: str) -> str:
    """Invokes the agent and returns the final assistant message content."""
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    last_message = result["messages"][-1]
    
    # Handle response content properly whether returned as string or content list
    if hasattr(last_message, "text"):
        return last_message.text
    elif isinstance(last_message.content, str):
        return last_message.content
    else:
        return str(last_message.content)


if __name__ == "__main__":
    test_questions = [
        "Where is my order KE1002?",
        "Can I pay cash for a ₹12,000 order?",
        "My return for KE1006 was picked up. When will I get my refund?",
        "What is the status of order KE9999?",
    ]

    print("=== Testing KartEase Support Agent ===\n")
    for q in test_questions:
        print(f"Q: {q}")
        print(f"A: {ask(agent, q)}")
        print("-" * 60)