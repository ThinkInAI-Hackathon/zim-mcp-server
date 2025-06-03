[English](README.md) | [中文](README.zh_CN.md) 

# ZIM MCP Server

[ZIM](https://en.wikipedia.org/wiki/ZIM_(file_format))（Zeno IMproved）是一种由[Kiwix](https://www.kiwix.org/)非营利组织开发的文件格式，专为离线存储和访问维基百科和其他大型参考内容而设计。ZIM 格式支持高压缩率和快速搜索，使得整个维基百科可以被压缩到相对较小的文件中，便于存储和使用，特别适合没有互联网连接的环境。

ZIM MCP Server 让大语言模型能够直接访问和搜索 ZIM 文件内容，使用户即使在离线环境下，也能通过本地 AI 模型对这些知识资源进行问答和信息检索。

## 关于 Kiwix

[Kiwix](https://www.kiwix.org/) 是一个非营利组织，致力于让互联网上的知识内容（如维基百科、TED 演讲等）可以离线访问。Kiwix 开发了用于创建、查看和搜索 ZIM 文件的工具，帮助用户将大量在线知识资源打包为 ZIM 文件进行本地访问。Kiwix 项目对于没有互联网连接的发展中国家和地区尤为重要，促进了知识普及和教育公平。

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/ThinkInAI-Hackathon/zim-mcp-server.git
```

### 2. 安装 `uv`

- Windows 下：
  - 如果未设置过执行策略，运行：
    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```
  - 否则可以直接运行：
    ```powershell
    irm https://astral.sh/uv/install.ps1 | iex
    ```
- MacOS 下：
  - 请参考 [官方 uv 安装指南](https://docs.astral.sh/uv/getting-started/installation/)

### 3. 安装依赖

```bash
cd path\to\zim-mcp-server   # （例如 D:\zim-mcp-server）
uv sync
```

### 4. 准备 ZIM 文件

从 [Kiwix Library](https://browse.library.kiwix.org/) 下载所需的 ZIM 文件（如维基百科、维基词典等），并放置到某个目录下，例如：

```
path\to\zim\files   # （例如 D:\ZIM）
```

---

## Claude Desktop 配置

Claude Desktop 需要使用本地克隆仓库的路径。

在 `claude_desktop_config.json` 中添加如下配置（请将路径替换为你的实际本地路径）：

```json
"zim-mcp-server": {
  "command": "uv",
  "args": [
    "--directory",
    "path\\to\\zim-mcp-server",   // 例如 D:\\zim-mcp-server
    "run",
    "server.py",
    "path\\to\\zim\\files"      // 例如 D:\\ZIM
  ]
}
```
- `"path\\to\\zim-mcp-server"`：本地 zim-mcp-server 仓库路径（如 D:\\zim-mcp-server）
- `"path\\to\\zim\\files"`：ZIM 文件目录（如 D:\\ZIM）

只有完成此配置后，Claude Desktop 才能识别并连接到该服务。

---

## 可用工具

### list_zim_files - 列出所有允许目录中的 ZIM 文件

无需参数。

### search_zim_file - 在 ZIM 文件内容中搜索

**必需参数：**
- `zimFilePath`（字符串）：ZIM 文件路径
- `query`（字符串）：搜索关键词

**可选参数：**
- `limit`（整数，默认 10）：返回的最大结果数
- `offset`（整数，默认 0）：结果的起始偏移量（用于分页）

### get_zim_entry - 获取 ZIM 文件中特定条目的详细内容

**必需参数：**
- `zimFilePath`（字符串）：ZIM 文件路径
- `entryPath`（字符串）：条目路径，如 'A/Some_Article'

**可选参数：**
- `maxContentLength`（整数，默认 100000）：返回内容的最大长度

---

## 示例

### 列出 ZIM 文件：
```json
{
  "name": "list_zim_files"
}
```

响应：
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

### 搜索 ZIM 文件：
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

响应：
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

### 获取 ZIM 条目：
```json
{
  "name": "get_zim_entry",
  "arguments": {
    "zimFilePath": "D:/ZIM/wikipedia_en_all_nopic_2023-07.zim",
    "entryPath": "A/Artificial_intelligence"
  }
}
```

响应：
```
# Artificial intelligence

Path: A/Artificial_intelligence
Type: text/html
## Content

Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to intelligence displayed by humans or by other animals. Examples of specific artificial intelligence applications include expert systems, natural language processing, and computer vision.

Leading AI textbooks define the field as the study of "intelligent agents": any system that perceives its environment and takes actions that maximize its chance of achieving its goals. Some popular accounts use the term "artificial intelligence" to describe machines that mimic "cognitive" functions that humans associate with the human mind, such as "learning" and "problem solving".

...
```

---

## License

MIT
