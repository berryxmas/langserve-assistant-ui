from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from langserve import add_routes
from .react_agent import agent_executor
from pydantic import BaseModel
from typing import List, Union, Dict, Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import os
from fastapi.middleware.cors import CORSMiddleware
import json
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio


class ChatInputType(BaseModel):
    messages: List[Union[HumanMessage, AIMessage, SystemMessage]]

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Mount the invoices directory to serve PDF files
invoice_dir = "backend/invoices"
if not os.path.exists(invoice_dir):
    os.makedirs(invoice_dir)
app.mount("/invoices", StaticFiles(directory=invoice_dir), name="invoices")


@app.get("/invoices/{filename}")
async def get_invoice(filename: str):
    file_path = os.path.join(invoice_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Invoice not found")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)


# Edit this to add the chain you want to add
prebuilt_react_agent_runnable = agent_executor.with_types(input_type=ChatInputType)
add_routes(app, prebuilt_react_agent_runnable, path="/agent")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
