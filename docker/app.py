import os
import asyncio
import time
import logging
from typing import List, Union, Optional
import torch

# Prevent multi-threading lockups
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

torch.set_num_threads(1)
if hasattr(torch, "set_num_interop_threads"):
    try:
        torch.set_num_interop_threads(1)
    except Exception:
        pass

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("embedder")

MODEL_ID = os.environ.get("MODEL_NAME", "PruhaNLP/USER2-1C-code")
PORT = int(os.environ.get("PORT", "8000"))
DEFAULT_DIM = int(os.environ.get("DEFAULT_DIM", "256"))
INFERENCE_BATCH_SIZE = int(os.environ.get("BATCH_SIZE", "64"))
MAX_SEQ_LENGTH = int(os.environ.get("MAX_SEQ_LENGTH", "4096"))

app = FastAPI(title="USER2-1C-code Embedding Server", version="1.0.0")

gpu_lock = asyncio.Lock()
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

logger.info(f"Loading '{MODEL_ID}' on device '{device}' ({dtype})...")
model = SentenceTransformer(MODEL_ID, device=device, model_kwargs={"torch_dtype": dtype})
if hasattr(model, "max_seq_length"):
    model.max_seq_length = MAX_SEQ_LENGTH
logger.info(f"Model ready. Default dim: {DEFAULT_DIM}, Batch: {INFERENCE_BATCH_SIZE}, Device: {device}")


class EmbeddingsRequest(BaseModel):
    model: Optional[str] = None
    input: Union[str, List[str]]
    dimensions: Optional[int] = None


@app.get("/health")
@app.get("/")
async def health():
    allocated = round(torch.cuda.memory_allocated() / (1024**2), 1) if torch.cuda.is_available() else 0
    reserved = round(torch.cuda.memory_reserved() / (1024**2), 1) if torch.cuda.is_available() else 0
    return {
        "status": "ok",
        "model": MODEL_ID,
        "device": device,
        "default_dim": DEFAULT_DIM,
        "batch_size": INFERENCE_BATCH_SIZE,
        "vram_allocated_mb": allocated,
        "vram_reserved_mb": reserved,
    }


@app.get("/v1/models")
async def list_v1_models():
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_ID,
                "object": "model",
                "owned_by": "organization_owner",
            }
        ],
    }


def _sync_encode(texts: List[str], dim: int):
    with torch.inference_mode():
        return model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=min(len(texts), INFERENCE_BATCH_SIZE),
            truncate_dim=dim,
        )


@app.post("/v1/embeddings")
async def create_embeddings(req: EmbeddingsRequest):
    texts = [req.input] if isinstance(req.input, str) else req.input
    if not texts:
        return {"object": "list", "data": [], "model": MODEL_ID}

    t0 = time.perf_counter()
    dim = req.dimensions if req.dimensions and req.dimensions <= 768 else DEFAULT_DIM

    try:
        async with gpu_lock:
            embeddings = await asyncio.to_thread(_sync_encode, texts, dim)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    except Exception as e:
        logger.error(f"Error during embedding generation: {e}", exc_info=True)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return JSONResponse(status_code=500, content={"error": {"message": str(e), "type": "server_error"}})

    data = [
        {
            "object": "embedding",
            "index": i,
            "embedding": emb.tolist(),
        }
        for i, emb in enumerate(embeddings)
    ]

    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"Processed {len(texts)} texts in {elapsed_ms:.1f}ms (dim: {dim})")

    return {
        "object": "list",
        "data": data,
        "model": MODEL_ID,
        "usage": {
            "prompt_tokens": len(texts),
            "total_tokens": len(texts),
        },
    }
