[English](README.md) | [中文](README.zh_CN.md)

# ZIM MCP Server

[ZIM](https://en.wikipedia.org/wiki/ZIM_(file_format)) (Zeno IMproved) is a file format developed by the nonprofit organization [Kiwix](https://www.kiwix.org/), designed specifically for offline storage and access to Wikipedia and other large reference content. The ZIM format supports high compression rates and fast searching, enabling entire Wikipedia content to be compressed into relatively small files for convenient storage and use, especially in environments without internet connectivity.

ZIM MCP Server provides large language models with the ability to directly access and search content within ZIM files, allowing people to use local AI models for question answering and information retrieval from these offline knowledge resources, even without network access.

## About Kiwix

[Kiwix](https://www.kiwix.org/) is a nonprofit organization dedicated to making online knowledge content (especially Wikipedia, TED talks, etc.) accessible offline. Kiwix has developed tools for creating, viewing, and searching ZIM files, through which people can package large amounts of online knowledge resources into ZIM files for local access. The Kiwix project is particularly important for developing countries and regions without internet connectivity, as it enables people in these areas to access rich knowledge resources, promoting the dissemination of knowledge and equal educational opportunities.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ThinkInAI-Hackathon/zim-mcp-server.git
```

### 2. Install `uv`

- On Windows:
  - If you have not set execution policy before, run:
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```
  - Otherwise, you can run:
    ```powershell
    irm https://astral.sh/uv/install.ps1 | iex
    ```
- On MacOS:
  - Please refer to the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### 3. Install Dependencies

```bash
cd path\to\zim-mcp-server   # (e.g., D:\zim-mcp-server)
uv sync
```

### 4. Prepare ZIM Files

Download ZIM files (e.g., Wikipedia, Wiktionary, etc.) from the [Kiwix Library](https://browse.library.kiwix.org/) and place them in a directory, e.g.,

```
path\to\zim\files   # (e.g., D:\ZIM)
```

---

## Configuration for Claude Desktop

The configuration for Claude Desktop requires the local path to your cloned repository.

Add the following to your `claude_desktop_config.json` (replace the paths with your actual local paths):

```json
"zim-mcp-server": {
  "command": "uv",
  "args": [
    "--directory",
    "path\\to\\zim-mcp-server",   // e.g., D:\\zim-mcp-server
    "run",
    "server.py",
    "path\\to\\zim\\files"      // e.g., D:\\ZIM
  ]
}
```
- `"path\\to\\zim-mcp-server"`: Local path to your cloned zim-mcp-server repository (e.g., D:\\zim-mcp-server).
- `"path\\to\\zim\\files"`: Directory containing your ZIM files (e.g., D:\\ZIM).

Claude Desktop will recognize the server only after this configuration.

---

## Available Tools

### list_zim_files - List all ZIM files in allowed directories

No parameters required.

### search_zim_file - Search within ZIM file content

**Required parameters:**
- `zimFilePath` (string): Path to the ZIM file
- `query` (string): Search query term

**Optional parameters:**
- `limit` (integer, default: 10): Maximum number of results to return
- `offset` (integer, default: 0): Starting offset for results (for pagination)

### get_zim_entry - Get detailed content of a specific entry in a ZIM file

**Required parameters:**
- `zimFilePath` (string): Path to the ZIM file
- `entryPath` (string): Entry path, e.g., 'A/Some_Article'

**Optional parameters:**
- `maxContentLength` (integer, default: 100000): Maximum length of returned content

---

## Examples

### Listing ZIM files:
```json
{
  "name": "list_zim_files"
}
```

Response:
```
{
  "Found 2 ZIM files in 1 directories:

  [
    {
      "name": "wikipedia_en_all_nopic_2023-07.zim",
      "path": "D:/ZIM/wikipedia_en_all_nopic_2023-07.zim",
      "directory": "D:/ZIM",
      "size": "95123.45 MB",
      "modified": "2023-08-01T12:00:00"
    },
    {
      "name": "wiktionary_en_all_nopic_2023-07.zim",
      "path": "D:/ZIM/wiktionary_en_all_nopic_2023-07.zim",
      "directory": "D:/ZIM",
      "size": "1234.56 MB",
      "modified": "2023-08-01T12:30:00"
    }
  ]
}
```

### Searching ZIM files:
```json
{
  "name": "search_zim_file",
  "arguments": {
    "zimFilePath": "D:/ZIM/wikipedia_en_all_nopic_2023-07.zim",
    "query": "artificial intelligence",
    "limit": 3
  }
}
```

Response:
```
Found 120 matches for "artificial intelligence", showing 1-3:

## 1. Artificial intelligence
Path: A/Artificial_intelligence
Snippet: Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to intelligence displayed by humans or by other animals. ...

## 2. History of artificial intelligence
Path: A/History_of_artificial_intelligence
Snippet: The history of artificial intelligence (AI) began in antiquity, with myths, stories and rumors of artificial beings endowed with intelligence or consciousness by master craftsmen. ...

## 3. Philosophy of artificial intelligence
Path: A/Philosophy_of_artificial_intelligence
Snippet: The philosophy of artificial intelligence is a branch of the philosophy of technology that explores artificial intelligence and its implications for knowledge, reality, consciousness, and the human mind. ...
```

### Getting ZIM entries:
```json
{
  "name": "get_zim_entry",
  "arguments": {
    "zimFilePath": "D:/ZIM/wikipedia_en_all_nopic_2023-07.zim",
    "entryPath": "A/Artificial_intelligence"
  }
}
```

Response:
```
# Artificial intelligence

Path: A/Artificial_intelligence
Type: text/html
## Content

Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to intelligence displayed by humans or by other animals. Examples of specific artificial intelligence applications include expert systems, natural language processing, and computer vision.

Leading AI textbooks define the field as the study of "intelligent agents": any system that perceives its environment and takes actions that maximize its chance of achieving its goals. Some popular accounts use the term "artificial intelligence" to describe machines that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".

...
```

## License

MIT