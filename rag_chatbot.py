from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.document_loaders import TextLoader
import torch
from huggingface_hub import login
from pathlib import Path
from config import get_token

class RAGChatbot:
    def __init__(self, model_dir=None, docs_dir="./docs"):
        print("Initializing RAG Chatbot...")
        self.model_dir = Path(model_dir) if model_dir else None
        self.setup_model()
        self.setup_vectorstore(docs_dir)
        self.setup_prompt_template()

    def setup_model(self):
        print("Loading language model...")
        token = get_token()
        login(token=token)

        model_name = "mistralai/Mistral-7B-Instruct-v0.1"

        if self.model_dir:
            self.model_dir.mkdir(parents=True, exist_ok=True)
            print(f"Using model directory: {self.model_dir}")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=self.model_dir
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
            cache_dir=self.model_dir
        )

        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=512,
            temperature=0.7,
        )

    def load_documents(self, docs_dir):
        """Load documents without using DirectoryLoader"""
        documents = []
        docs_path = Path(docs_dir)
        
        # Recursively find all .txt files
        for file_path in docs_path.rglob("*.txt"):
            try:
                loader = TextLoader(str(file_path))
                documents.extend(loader.load())
                print(f"Loaded: {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                
        return documents

    def setup_vectorstore(self, docs_dir):
        print("Setting up vector store...")
        vector_store_dir = Path("vector_store")
        vector_store_dir.mkdir(exist_ok=True)

        # Initialize embeddings first as we need it in both cases
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )

        # Try to load existing vector store
        try:
            if list(vector_store_dir.glob("*.faiss")):
                print("Loading existing vector store...")
                self.vectorstore = FAISS.load_local(
                    "vector_store",
                    self.embeddings
                )
                return
        except Exception as e:
            print(f"Could not load existing vector store: {e}")

        print("Creating new vector store...")
        documents = self.load_documents(docs_dir)
        if not documents:
            raise Exception("No documents found in the specified directory")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        
        # Save vector store
        self.vectorstore.save_local("vector_store")

    def setup_prompt_template(self):
        self.template = """<s>[INST] Answer the question based only on the given context. If you can't find the answer in the context, say so.
        Context: {context}
        Question: {question} [/INST]
        """
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.template
        )

    def get_response(self, question):
        relevant_docs = self.vectorstore.similarity_search(question, k=3)
        context = "\n".join(doc.page_content for doc in relevant_docs)
        augmented_prompt = self.prompt.format(
            context=context,
            question=question
        )
        response = self.pipe(augmented_prompt)[0]['generated_text']
        response = response.split('[/INST]')[-1].strip()
        sources = [doc.metadata.get('source', 'Unknown source') for doc in relevant_docs]
        return response, sources, context