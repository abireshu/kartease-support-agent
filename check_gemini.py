import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env
load_dotenv()

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing. Check your .env file.")

    # Initialize Gemini LLM using LangChain
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0
    )

    # Send a single test prompt
    prompt = "Hello! Confirm that the KartEase support assistant environment is active."
    print(f"Sending prompt to Gemini ({model_name})...\n")
    
    response = llm.invoke(prompt)
    
    print("--- Gemini Response ---")
    print(response.content)
    print("-----------------------")

if __name__ == "__main__":
    main()