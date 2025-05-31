from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import os

# Load environment variables from .env
load_dotenv()

# Load Hugging Face embeddings and FAISS vectorstore
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(os.path.join(os.path.dirname(__file__), "faiss_index"), embeddings, allow_dangerous_deserialization=True)

# Prompt template
prompt_template = """
You are a compassionate and friendly nurse helping a patient understand their health condition. Use only the given context to answer the patient's medical question.
Speak in warm, simple, and reassuring language. Avoid just listing facts — instead, explain them in a way that's easy to understand and caring.


If the answer is not in the context, say "I'm sorry, I don't have enough information to answer that based on the available material."

Context:
{context}

Question:
{question}

Answer:
"""

PROMPT = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

# Load Groq LLM (Mixtral or LLaMA3 works)
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-8b-8192",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)


# Create QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=db.as_retriever(search_kwargs={"k": 4}),
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=False
)


# Final function
def answer_question(question: str) -> str:
    return qa_chain.invoke({"query": question})["result"]