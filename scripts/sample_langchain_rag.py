#!/usr/bin/env python3
"""Sample LangChain RAG pipeline for document retrieval and generation."""

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
import os

# Mock documents - replace with actual data loading
sample_docs = [
    Document(page_content="AI development requires careful testing and validation."),
    Document(page_content="FastAPI is great for building APIs with Pydantic validation."),
    Document(page_content="LangChain helps with retrieval-augmented generation.")
]

def create_rag_pipeline():
    """Create a simple RAG pipeline."""
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

    # Split documents
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(sample_docs)

    # Create vector store
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Create retriever
    retriever = vectorstore.as_retriever()

    # Create LLM
    llm = ChatOpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))

    # Create RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain

def main():
    """Run a sample query."""
    qa_chain = create_rag_pipeline()

    query = "What is FastAPI?"
    result = qa_chain({"query": query})

    print("Query:", query)
    print("Answer:", result["result"])
    print("Sources:", [doc.page_content for doc in result["source_documents"]])

if __name__ == "__main__":
    main()
