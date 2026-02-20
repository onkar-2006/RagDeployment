from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List

class PDFIAndURLIngestor:
    def __init__(self):
        pass

    def load_pdf(self, file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        return text_splitter.split_documents(documents)
        
    def load_url(self, url: str) -> List[Document]:
        loader = WebBaseLoader(url)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
        return text_splitter.split_documents(documents)


    
