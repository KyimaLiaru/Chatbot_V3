from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from typing import List, Dict, Any

import shutil
import json
import os


# Setup Embedding Model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def sanitize_metadata(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Only allow str, int, float, bool, or None values in metadata."""
    clean = {}
    for k, v in entry.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            clean[k] = v
        elif isinstance(v, list) and all(isinstance(i, (str, int, float, bool)) for i in v):
            clean[k] = str(v)  # convert list to string
        elif isinstance(v, dict):
            clean[k] = str(v)  # convert nested dict to string
        else:
            clean[k] = str(v)
    return clean


# ─────────────────────────────────────────────────────────────────────────────

def preprocessManual(json_path, persist_dir):
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    for entry in data:
        parts = []
        if "question_en" in entry:
            parts.append(entry["question_en"])
        if "answer_en" in entry:
            parts.append(entry["answer_en"])
        if parts:
            content = " ".join(parts)
            documents.append(Document(page_content=content))

    if not documents:
        raise ValueError(f"No usable content found in {json_path} for vectorstore!")

    unique_docs = list({doc.page_content: doc for doc in documents}.values())

    vectorstore = Chroma.from_documents(
        unique_docs,
        embedding=embedding_model,
        persist_directory=persist_dir
    )
    return vectorstore


# ─────────────────────────────────────────────────────────────────────────────

def preprocessApiSpecs(json_path, persist_dir):
    # from langchain_community.vectorstores.utils import filter_complex_metadata

    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    for entry in data:
        # Create readable text from API info and parameters
        api_name = entry.get("api_name_en", "")
        api_path = entry.get("api_path", "")
        api_method = entry.get("method", "")
        api_url = entry.get("api_url", "")

        parameters = entry.get("parameters", [])
        param_texts = []
        if isinstance(parameters, list):
            for param in parameters:
                if isinstance(param, dict):
                    key = param.get("key", "")
                    desc = param.get("description_en", "")
                    dtype = param.get("datatype", "")
                    ptype = param.get("type", "")
                    required = param.get("required", "")
                    param_texts.append(
                        f"\tKey: {key}, Description: {desc}, Type: {ptype}, Datatype: {dtype}, Required: {required}"
                    )
        param_summary = "\n".join(param_texts)

        full_text = f"""
API Name: {api_name}
API URL: {api_url}{api_path}
Method: {api_method}
Parameters:
{param_summary}
""".strip()

        # Keep only simple metadata
        simple_metadata = {
            "id": entry.get("id"),
            "api_name": api_name,
            "api_path": api_path,
            "method": api_method,
        }

        documents.append(Document(page_content=full_text, metadata=simple_metadata))

    if not documents:
        raise ValueError(f"No usable API content found in {json_path}")

    vectorstore = Chroma.from_documents(
        documents,
        embedding=embedding_model,
        persist_directory=persist_dir
    )
    return vectorstore

def loadManual():
    return preprocessManual("fireone_product_qa_combined_translated gpt.json", "chromaManualDB")

def loadApiSpecs():
    return preprocessApiSpecs("FireOne_API_List_v2.json", "chromaApiSpecsDB")