# LM Studio Embedding MCP Server

Universal [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for generating text and code embeddings via [LM Studio](https://lmstudio.ai/).

Works with any embedding model loaded in LM Studio (`USER2-1C-code`, `nomic-embed-text`, `bge-m3`, `multilingual-e5`, etc.) across all major AI coding environments and agents.

---

## Features

- **`lmstudio_embed`**: Generates high-dimensional vector embeddings for code snippets, docstrings, or natural language queries.
- **`lmstudio_list_models`**: Lists all models currently available or loaded in LM Studio.
- **Zero external dependencies**: Built purely using the Python standard library (`sys`, `json`, `urllib`).
- **Cross-platform**: Works on Windows, macOS, and Linux. Supports both local instances (`127.0.0.1:1234`) and remote instances over SSH tunnels / LAN.

---

## Prerequisites

1. **Python 3.10+** installed.
2. **LM Studio** running with an embedding model loaded:
   - In LM Studio, load your model (e.g. `USER2-1C-code` or `nomic-embed-text-v1.5`).
   - Go to the **Developer / Local Server** tab (`<->`) and start the server on port `1234`.
   - *Note for ModernBERT models:* In **My Models**, under **Domain Control**, ensure the domain is set to **Text Embedding**.

---

## Configuration for Popular Environments

### 1. Google Antigravity / Gemini Code Assist

Add the server to your Antigravity configuration file (`~/.gemini/config/mcp_config.json`):

```json
{
  "mcpServers": {
    "lmstudio-embedding": {
      "command": "python",
      "args": [
        "C:/path/to/lmstudio-embedding-mcp/server.py",
        "--url",
        "http://127.0.0.1:1234",
        "--model",
        "user2-1c-code"
      ]
    }
  }
}
```

---

### 2. OpenCode Interpreter / OpenCode CLI

Add the server to `opencode.json` (or `~/.config/opencode/config.json`):

```json
{
  "mcp": {
    "servers": {
      "lmstudio": {
        "type": "stdio",
        "command": "python",
        "args": [
          "/path/to/lmstudio-embedding-mcp/server.py",
          "--url",
          "http://127.0.0.1:1234"
        ]
      }
    }
  }
}
```

---

### 3. Claude Desktop

Add to `claude_desktop_config.json`:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "lmstudio-embedding": {
      "command": "python",
      "args": [
        "/path/to/lmstudio-embedding-mcp/server.py",
        "--url",
        "http://127.0.0.1:1234",
        "--model",
        "user2-1c-code"
      ]
    }
  }
}
```

---

### 4. Cursor IDE

In Cursor:
1. Open **Settings** -> **Features** -> **MCP**.
2. Click **+ Add New MCP Server**.
3. Set:
   - **Name:** `lmstudio-embedding`
   - **Type:** `command`
   - **Command:** `python C:/path/to/lmstudio-embedding-mcp/server.py --url http://127.0.0.1:1234`

Or edit `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "lmstudio-embedding": {
      "command": "python",
      "args": [
        "C:/path/to/lmstudio-embedding-mcp/server.py",
        "--url",
        "http://127.0.0.1:1234"
      ]
    }
  }
}
```

---

### 5. Windsurf / Codeium

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "lmstudio-embedding": {
      "command": "python",
      "args": [
        "C:/path/to/lmstudio-embedding-mcp/server.py",
        "--url",
        "http://127.0.0.1:1234"
      ]
    }
  }
}
```

---

### 6. Continue.dev (VS Code / JetBrains)

In `~/.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "python",
          "args": [
            "C:/path/to/lmstudio-embedding-mcp/server.py",
            "--url",
            "http://127.0.0.1:1234"
          ]
        }
      }
    ]
  }
}
```

---

## Command Line Options

| Flag | Default | Description |
|---|---|---|
| `--url` | `http://127.0.0.1:1234` | Base URL of the LM Studio REST API server |
| `--model` | `user2-1c-code` | Default model ID used when `model` argument is omitted in tool call |

---

## Remote Usage (SSH Tunnel)

If LM Studio is running on another machine (e.g. `10.0.1.1`):

```bash
# Forward remote port 1234 to local port 1234
ssh -L 1234:127.0.0.1:1234 user@10.0.1.1 -N
```

Then configure the MCP server pointing to `http://127.0.0.1:1234`.

---

## License

MIT License. Free for personal and commercial use.
