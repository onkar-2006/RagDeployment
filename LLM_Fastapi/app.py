from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware  
from typing import Optional
import tempfile
import os
from langchain_core.messages import HumanMessage
from Agent.agent import app as agent_app
from Ingestion.Data_ingestion import PDFIAndURLIngestor
from VectorStore.Vector_Store import VectorStore
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:5174",  
    "http://127.0.0.1:5174",
    "https://ragdeployment.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         
    allow_credentials=True,
    allow_methods=["*"],             
    allow_headers=["*"],              
)
# ---------------------------

ingestor = PDFIAndURLIngestor()
vs_manager = VectorStore()

@app.post("/api/chat")
async def chat_with_agent(
    question: str = Form(...),          
    url: Optional[str] = Form(None),   
    pdf_file: Optional[UploadFile] = File(None) 
):
    try:
        all_docs = []

        if pdf_file and pdf_file.filename != "":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                content = await pdf_file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            pdf_docs = ingestor.load_pdf(tmp_path)
            all_docs.extend(pdf_docs)
            os.remove(tmp_path) 

        if url and url.lower() != "string" and url.startswith("http"):
            url_docs = ingestor.load_url(url)
            all_docs.extend(url_docs)

        if all_docs:
            vs_manager.load_vectorStore(docs=all_docs)

        inputs = {"messages": [HumanMessage(content=question)]}
        result = await agent_app.ainvoke(inputs)
        
        return {
            "answer": result["messages"][-1].content,
            "has_docs": len(all_docs) > 0
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

