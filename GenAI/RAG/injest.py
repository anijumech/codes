'''
                         ┌─────────────────┐
                         │ DevOps Documents│
                         └────────┬────────┘
                                  │
                                  ↓
                             Load Documents
                                  │
                                  ↓
                               Chunking
                                  │
                                  ↓
                             Embeddings
                                  │
                                  ↓
                         ┌─────────────────┐
                         │ Vector Database │
                         └────────-────────┘

'''

from pypdf import PdfReader
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


# Load the pdf documents
text = ""
files = Path("./docs").glob("*.pdf")
for file in files:
     data = PdfReader(file)
     for page in data.pages:
          text += page.extract_text()


# Chunk the texts extracted
documents = []
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=100)
chunks = text_splitter.split_text(text)

for index, chunk in enumerate(chunks):
     documents.append(Document(chunk))


# Store the Chunks in the Vector DB
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
chromaDB = Chroma(collection_name="devops_documents" , embedding_function=embedding_model, persist_directory="./chromadb")
chromaDB.add_documents(documents)


