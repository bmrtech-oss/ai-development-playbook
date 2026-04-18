import os
import re
import chromadb
from github import Github
from openai import OpenAI
import tiktoken
import markdown

def chunk_markdown_by_headings(content):
    """Chunk markdown content by headings."""
    chunks = []
    lines = content.split('\n')
    current_chunk = []
    for line in lines:
        if re.match(r'^#{1,6} ', line):
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
        current_chunk.append(line)
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
    return chunks

def load_docs_into_chroma():
    """Load all .md files from docs/ into Chroma vector store."""
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="playbook_docs")

    for root, dirs, files in os.walk('docs'):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                chunks = chunk_markdown_by_headings(content)
                for i, chunk in enumerate(chunks):
                    embedding = get_embedding(chunk)
                    collection.add(
                        documents=[chunk],
                        metadatas=[{"source": filepath, "chunk": i}],
                        ids=[f"{filepath}_chunk_{i}"],
                        embeddings=[embedding]
                    )
    return collection

def get_embedding(text):
    """Generate embedding using OpenAI."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def retrieve_relevant_chunks(query, collection, top_k=5):
    """Retrieve relevant chunks for the query."""
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0], results['metadatas'][0]

def generate_answer(query, context_chunks, sources):
    """Generate answer using OpenAI."""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    context = "\n\n".join(context_chunks)
    prompt = f"""
    You are the Playbook Copilot, an AI assistant for the AI Development Playbook repository.
    Answer the user's question based on the provided context from the playbook documentation.
    Be concise, actionable, and cite sources when relevant.

    Context:
    {context}

    Question: {query}

    Answer:
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    answer = response.choices[0].message.content

    # Add source citations
    citations = "\n\nSources:\n" + "\n".join([f"- [{os.path.basename(src['source'])}]({src['source']})" for src in sources])
    return answer + citations

def post_comment(issue_number, answer):
    """Post answer as comment on the issue."""
    g = Github(os.getenv('GITHUB_TOKEN'))
    repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))
    issue = repo.get_issue(number=issue_number)
    issue.create_comment(answer)

def main():
    # Extract question from comment
    comment_body = os.getenv('GITHUB_EVENT_COMMENT_BODY', '')
    question = comment_body.split('/ask', 1)[1].strip() if '/ask' in comment_body else ''

    if not question:
        return

    # Load docs
    collection = load_docs_into_chroma()

    # Retrieve context
    chunks, sources = retrieve_relevant_chunks(question, collection)

    # Generate answer
    answer = generate_answer(question, chunks, sources)

    # Post comment
    issue_number = int(os.getenv('GITHUB_EVENT_ISSUE_NUMBER', 0))
    post_comment(issue_number, answer)

if __name__ == "__main__":
    main()