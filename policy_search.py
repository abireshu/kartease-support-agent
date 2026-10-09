import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from ingest import get_vectorstore

load_dotenv()

SORRY = "Sorry, I can only help with KartEase orders and policies."

# Temperature=0 ensures deterministic, consistent, and hallucination-free output
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)

store = get_vectorstore()
retriever = store.as_retriever(search_kwargs={"k": 3})

PROMPT = """You are a KartEase customer support assistant.
Answer the question using ONLY the context provided below.
- Keep the answer short, clear, and friendly.
- End with the source file name(s) you used, like: (Source: returns_and_refunds.md)
- If the context does not contain enough information to answer the question, or if the question is off-topic, reply EXACTLY:
  {sorry}

Context:
{context}

Question: {question}
"""


def search_policies(question: str) -> str:
    """Answer questions about KartEase policies (returns, refunds, shipping,
    delivery, warranty, payments, COD, coupons) from the policy documents."""
    docs = retriever.invoke(question)
    
    # Format chunks with explicit source citations in the context payload
    context = "\n\n".join(
        f"\n{d.page_content}" for d in docs
    )
    
    formatted_prompt = PROMPT.format(sorry=SORRY, context=context, question=question)
    
    # .text guarantees string output regardless of response payload format
    response = llm.invoke(formatted_prompt)
    return response.content if isinstance(response.content, str) else str(response.content)


if __name__ == "__main__":
    tests = [
        "How many days do I have to return a phone?",
        "What is the delivery charge on a ₹350 order?",
        "Can I pay cash on delivery for a ₹12,000 order?",
        "Who won the World Cup?",
        "Write me a poem about Diwali.",
    ]
    
    print("=== Testing Policy Search Function ===\n")
    for q in tests:
        print(f"Q: {q}")
        print(f"A: {search_policies(q)}")
        print("-" * 60)