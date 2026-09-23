# Official high-performance C++ embedding server based on llama.cpp (CUDA enabled)
FROM ghcr.io/ggml-org/llama.cpp:server-cuda

# Model file will be mounted via volume into /models/model.gguf
# Or downloaded during startup if MODEL_URL is provided

ENV LLAMA_ARG_HOST=0.0.0.0 \
    LLAMA_ARG_PORT=8000 \
    LLAMA_ARG_CTX_SIZE=8192 \
    LLAMA_ARG_EMBEDDINGS=1 \
    LLAMA_ARG_UBATCH_SIZE=512

EXPOSE 8000

ENTRYPOINT ["llama-server", "-m", "/models/model.gguf", "--embedding", "--pooling", "cls", "-c", "8192", "--host", "0.0.0.0", "--port", "8000"]
