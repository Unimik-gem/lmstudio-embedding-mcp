# LM Studio Embedding MCP Server

Универсальный сервер [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) для генерации векторных эмбеддингов текста и исходного кода через локальный [LM Studio](https://lmstudio.ai/).

Работает с любыми моделями эмбеддингов, загруженными в LM Studio (включая специализированную модель для 1С:Предприятие [USER2-1C-code-GGUF](https://huggingface.co/Unimikes/USER2-1C-code-GGUF), а также `nomic-embed-text`, `bge-m3`, `multilingual-e5` и др.), во всех современных средах разработки и ИИ-агентах.

---

## Возможности

- **`lmstudio_embed`** — расчет векторных представлений (эмбеддингов) для кода, поисковых запросов и произвольного текста.
- **`lmstudio_list_models`** — просмотр списка загруженных и доступных моделей в LM Studio.
- **Чистый Python (Zero dependencies)** — работает только на стандартной библиотеке Python (`sys`, `json`, `urllib`), установка сторонних `pip`-пакетов не требуется.
- **Кроссплатформенность** — Windows, macOS, Linux. Поддерживает как локальный запуск (`127.0.0.1:1234`), так и удаленный инстанс через SSH-туннель или локальную сеть.

---

## Предварительные требования

1. **Python 3.10+**
2. **LM Studio** с запущенным локальным сервером:
   * Загрузите модель эмбеддингов (например, [USER2-1C-code-GGUF](https://huggingface.co/Unimikes/USER2-1C-code-GGUF) или `nomic-embed-text-v1.5`).
   * Перейдите во вкладку **Developer / Local Server** (`<->`) и запустите сервер на порту `1234`.
   * *Примечание для моделей ModernBERT:* Во вкладке **My Models** выберите модель и в секции **Domain Control** убедитесь, что выбран тип **Text Embedding**.

---

## Настройка в популярных средах разработки

### 1. Google Antigravity / Gemini Code Assist

Добавьте конфигурацию в файл `~/.gemini/config/mcp_config.json`:

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

Добавьте в `opencode.json` (или `~/.config/opencode/config.json`):

```json
{
  "mcp": {
    "servers": {
      "lmstudio": {
        "type": "stdio",
        "command": "python",
        "args": [
          "C:/path/to/lmstudio-embedding-mcp/server.py",
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

Добавьте в `claude_desktop_config.json`:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

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

### 4. Cursor IDE

1. Откройте **Settings** -> **Features** -> **MCP**.
2. Нажмите **+ Add New MCP Server**.
3. Укажите:
   - **Name:** `lmstudio-embedding`
   - **Type:** `command`
   - **Command:** `python C:/path/to/lmstudio-embedding-mcp/server.py --url http://127.0.0.1:1234`

Или отредактируйте `.cursor/mcp.json`:

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

Добавьте в `~/.codeium/windsurf/mcp_config.json`:

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

В файле `~/.continue/config.json`:

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

## Параметры командной строки

| Параметр | По умолчанию | Описание |
|---|---|---|
| `--url` | `http://127.0.0.1:1234` | Базовый URL сервера LM Studio |
| `--model` | `user2-1c-code` | Идентификатор модели по умолчанию (если не передан в аргументах вызова) |

---

## Работа с удаленным сервером (SSH-туннель)

Если LM Studio запущен на отдельном сервере или рабочей станции (например, `10.0.1.1`):

```bash
# Проброс удаленного порта 1234 на локальный порт 1234
ssh -L 1234:127.0.0.1:1234 user@10.0.1.1 -N
```

После этого в конфигурации любого MCP-клиента адрес остается локальным: `http://127.0.0.1:1234`.

---

<details>
<summary><b>English Version (Click to expand)</b></summary>

### Overview
Universal Model Context Protocol (MCP) server for generating text and code embeddings via LM Studio.

### Prerequisites
- Python 3.10+
- LM Studio running local server at port `1234`.

### Usage
Run directly:
```bash
python server.py --url http://127.0.0.1:1234 --model user2-1c-code
```

### CLI Flags
- `--url`: Base URL of the LM Studio REST API (default: `http://127.0.0.1:1234`).
- `--model`: Default embedding model ID (default: `user2-1c-code`).

### Tools Provided
- `lmstudio_embed`: Calculate embedding vectors for given text or code snippets.
- `lmstudio_list_models`: List available and loaded models.

</details>

---

## Лицензия

MIT License. Свободно для частного и коммерческого использования.
