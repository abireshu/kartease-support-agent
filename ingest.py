import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

DATA_DIR = "data"
CHROMA_DIR = "chroma_db"
COLLECTION = "kartease_policies"


def get_vectorstore():
    """Returns the Chroma vector store instance initialized with Gemini embeddings."""
    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GEMINI_EMBED_MODEL", "text-embedding-004"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    return Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )


def ingest():
    """Loads markdown files, splits them into chunks, and stores them in Chroma if not present."""
    store = get_vectorstore()

    # Requirement R1: Reuse stored vectors, do not embed again if count > 0
    if store._collection.count() > 0:
        print(f"Chroma already has {store._collection.count()} chunks. Skipping embedding.")
        return store

    print("Loading policy documents from data/...")
    loader = DirectoryLoader(
        DATA_DIR,
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    print(f"Loaded {len(docs)} documents.")

    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks.")

    # Preserve source_file in metadata for citations
    for c in chunks:
        c.metadata["source_file"] = os.path.basename(c.metadata["source"])

    store.add_documents(chunks)
    print("Embedded and stored chunks successfully in Chroma.")
    return store


if __name__ == "__main__":
    ingest()