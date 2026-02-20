import os
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()

os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")

class VectorStore:
    def __init__(self):
        self.index_name = "my-knowledge-base"
        self.pc = Pinecone(api_key=os.environ['PINECONE_API_KEY'])

    def load_vectorStore(self, docs=None): 
        if self.index_name not in [idx.name for idx in self.pc.list_indexes()]:
            self.pc.create_index(
                name=self.index_name,
                dimension=1536, 
                metric='cosine', 
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )

        embeddings = OpenAIEmbeddings(
            model="openai/text-embedding-3-small", 
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            check_embedding_ctx_length=False 
        )

        if docs:
            vectorstore = PineconeVectorStore.from_documents(
                documents=docs,
                embedding=embeddings,
                index_name=self.index_name
            )
        else:
            vectorstore = PineconeVectorStore(
                index_name=self.index_name,
                embedding=embeddings
            )

        return vectorstore.as_retriever(search_kwargs={"k": 3})
