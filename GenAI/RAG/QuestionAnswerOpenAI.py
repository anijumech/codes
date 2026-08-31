'''
User Question ──→ Embedding ──→ Similarity Search
                                  │
                                  ↓
                         Relevant Documents
                                  │
                                  ↓
                         Question + Context
                                  │
                                  ↓
                                LLM
                                  │
                                  ↓
                              Answer

'''
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from openai import OpenAI

# Get the question from user
question = input("what do you want to ask? ")

# Initialize the existing vector db
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_db = Chroma(collection_name="devops_documents" , embedding_function=embedding_model, persist_directory="./chromadb")

# Extract the most relevant results from the vector DB
results = vector_db.similarity_search(question, k=4)

# Join all the chunks together
all_chunks = "...\n...".join(item.page_content for item in results)

# Initialize the OpenAI

client = OpenAI()
final_query = "Here is the Context using RAG:" + all_chunks + "\n" + "Here is the Question from the User:" + question
response = client.responses.create(model="gpt-5.6-luna", input=final_query)
answer = response.output_text
print("Here is the Answer to you Question -> ", answer)
