import os
import asyncio
import glob
import numpy as np
import nest_asyncio
from lightrag.utils import EmbeddingFunc
from lightrag import LightRAG, QueryParam
from lightrag.llm import openai_complete_if_cache, openai_embedding
nest_asyncio.apply()
WORKING_DIR = "./dickens"

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
        api_key="EMPTY_KEY",
        base_url="BASE_URL",
        **kwargs,
    )

async def embedding_func(texts: list[str]) -> np.ndarray:
    return await openai_embedding(
        texts,
        model="model_name",
        api_key="EMPTY",
        base_url="BASE_URL",
    )

def get_text_files(dir_path):
    txt_files = glob.glob(os.path.join(dir_path, "*.txt"))
    return txt_files

async def main():
    try:
        rag = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=llm_model_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=1024, max_token_size=8192, func=embedding_func
            ),
        )
        text_files = get_text_files('files_path')
        for file_path in text_files:
            with open(file_path, "r", encoding="utf-8") as f:
                rag.insert(f.read())

        print(
            rag.query("介绍一下什么是ETF？", param=QueryParam(mode="local", top_k=10))
        )

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())