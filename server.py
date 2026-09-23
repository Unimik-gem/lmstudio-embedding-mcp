#!/usr/bin/env python3
"""
LM Studio Embedding MCP Server.

Universal Model Context Protocol (MCP) server for text embeddings via LM Studio.
Supports local (127.0.0.1:1234) and remote (SSH-tunneled) instances.

Features:
- `lmstudio_embed`: Generate text/code embeddings using any loaded embedding model in LM Studio.
- `lmstudio_list_models`: Inspect available and loaded models.

Compatible with:
- Antigravity / Gemini Code Assist
- OpenCode Interpreter / OpenCode CLI
- Claude Desktop
- Cursor / Windsurf / Continue.dev
"""

import sys
import json
import argparse
import urllib.request
import urllib.error

# Ensure UTF-8 for stdio communication
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def log(msg: str):
    sys.stderr.write(f"[lmstudio-mcp] {msg}\n")
    sys.stderr.flush()


class LMStudioClient:
    def __init__(self, base_url: str = "http://127.0.0.1:1234", default_model: str = "user2-1c-code"):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    def list_models(self) -> dict:
        url = f"{self.base_url}/v1/models"
        req = urllib.request.Request(url, headers={"User-Agent": "lmstudio-mcp"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {"error": f"Failed to connect to LM Studio at {url}: {e}"}

    def get_embeddings(self, text: str, model: str = None) -> dict:
        url = f"{self.base_url}/v1/embeddings"
        target_model = model or self.default_model
        payload = {
            "model": target_model,
            "input": text
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "lmstudio-mcp"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            return {"error": f"HTTP {e.code}: {err_body or e.reason}"}
        except Exception as e:
            return {"error": f"Failed to get embeddings from {url}: {e}"}


TOOLS = [
    {
        "name": "lmstudio_embed",
        "description": "Calculate text embedding vector via LM Studio. Works with any model loaded as Text Embedding (e.g. USER2-1C-code, nomic-embed, bge, e5).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text or code snippet to calculate embeddings for."
                },
                "model": {
                    "type": "string",
                    "description": "Model ID/name in LM Studio. If omitted, default model is used."
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "lmstudio_list_models",
        "description": "List loaded and available models in LM Studio.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def handle_rpc(client: LMStudioClient, msg: dict):
    req_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "lmstudio-embedding-mcp",
                    "version": "1.0.0"
                }
            }
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }

    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "lmstudio_list_models":
            data = client.list_models()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(data, indent=2, ensure_ascii=False)}
                    ]
                }
            }

        elif tool_name == "lmstudio_embed":
            text = args.get("text", "")
            model = args.get("model")
            res = client.get_embeddings(text, model)
            if "error" in res:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "isError": True,
                    "result": {
                        "content": [{"type": "text", "text": f"Error: {res['error']}"}]
                    }
                }

            data_arr = res.get("data", [])
            emb = data_arr[0].get("embedding", []) if data_arr else []
            dim = len(emb)
            sample = emb[:5] if dim > 0 else []
            summary = {
                "model": res.get("model", model or client.default_model),
                "embedding_dimension": dim,
                "sample_values_first_5": sample,
                "embedding": emb
            }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(summary, ensure_ascii=False)}
                    ]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "isError": True,
                "result": {
                    "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]
                }
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "isError": True,
        "result": {
            "content": [{"type": "text", "text": f"Unsupported method: {method}"}]
        }
    }


def main():
    parser = argparse.ArgumentParser(description="LM Studio Embedding MCP Server")
    parser.add_argument("--url", default="http://127.0.0.1:1234", help="LM Studio server base URL")
    parser.add_argument("--model", default="user2-1c-code", help="Default embedding model ID")
    args = parser.parse_args()

    client = LMStudioClient(base_url=args.url, default_model=args.model)
    log(f"Server started. Target: {args.url}, Default model: {args.model}")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as e:
            log(f"Invalid JSON: {e}")
            continue

        resp = handle_rpc(client, req)
        if resp is not None:
            out_line = json.dumps(resp, ensure_ascii=False)
            sys.stdout.write(out_line + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
