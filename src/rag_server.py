from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from lightrag import LightRAG, QueryParam
from lightrag.llm import openai_complete_if_cache, openai_embedding
from lightrag.utils import EmbeddingFunc
import numpy as np
from typing import Optional
import asyncio
import nest_asyncio

nest_asyncio.apply()

DEFAULT_RAG_DIR = "./dickens"
app = FastAPI()

WORKING_DIR = os.environ.get("RAG_DIR", f"{DEFAULT_RAG_DIR}")

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        "model_name",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key="EMPTY",
        base_url="BASE_URL",
        **kwargs,
    )

async def embedding_func(texts: list[str]) -> np.ndarray:
    return await openai_embedding(
        texts,
        model="model_name",
        api_key="EMPTY",
        base_url="base_url",
    )


rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=llm_model_func,
    embedding_func=EmbeddingFunc(
        embedding_dim=1024,
        func=embedding_func,
        max_token_size=8192
    ),
)


class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    only_need_context: bool = False


class Response(BaseModel):
    status: str
    data: Optional[str] = None
    message: Optional[str] = None



@app.post("/query", response_model=Response)
async def query_endpoint(request: QueryRequest):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: rag.query(
                request.query,
                param=QueryParam(
                    mode=request.mode, only_need_context=request.only_need_context
                ),
            ),
        )
        return Response(status="success", data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8020)
