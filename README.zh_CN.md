[English](README.md) | [中文](README.zh_CN.md) 

# ZIM MCP Server

[ZIM](https://en.wikipedia.org/wiki/ZIM_(file_format))（Zeno IMproved）是一种由[Kiwix](https://www.kiwix.org/)非营利组织开发的文件格式，专为离线存储和访问维基百科和其他大型参考内容而设计。ZIM格式支持高压缩率和快速搜索，使得整个维基百科可以被压缩到相对较小的文件中，便于存储和使用，特别是在没有互联网连接的环境中。

ZIM MCP Server 提供了让大语言模型直接访问和搜索 ZIM 文件中的内容的能力，让人们在没有网络的情况下，也能利用本地的AI大模型对这些离线的知识资源进行问答和信息检索。

## 关于 Kiwix

[Kiwix](https://www.kiwix.org/) 是一个非营利组织，致力于让互联网上的知识内容（特别是维基百科、TED 演讲等）可以离线访问。Kiwix 开发了用于创建、查看和搜索 ZIM 文件的工具，通过这些工具，人们可以将大量的在线知识资源打包成 ZIM 文件并在本地访问。Kiwix 项目对于没有互联网连接的发展中国家和地区尤为重要，它让这些地区的人们也能获取到丰富的知识资源，实现了知识的普及和教育机会的平等。


## 安装与运行

### 依赖

- [libzim 库](https://github.com/openzim/python-libzim)
- zim文件 - 可以从 [Kiwix Library](https://browse.library.kiwix.org/) 下载各种语言的维基百科、维基词典等 ZIM 文件

### 运行

注意指定包含 ZIM 文件的目录作为参数：

```bash
# 使用 uv 运行
uv --directory /path/to/repository run server.py /path/to/zim/files
```

## 配置

### 为 Claude, DeepChat等 配置

```json
{
  "command": "uv",
  "args": [
    "--directory",
    "/path/to/repository",
    "run", 
    "server.py",
    "/path/to/zim/files"
  ]
}
```

## 可用工具

### list_zim_files - 列出所有允许目录中的 ZIM 文件

不需要参数。

### search_zim_file - 在 ZIM 文件内容中搜索

**必需参数:**
- `zimFilePath` (字符串): ZIM 文件的路径
- `query` (字符串): 搜索查询词

**可选参数:**
- `limit` (整数, 默认值: 10): 返回的最大结果数
- `offset` (整数, 默认值: 0): 结果的起始偏移量（用于分页）

### get_zim_entry - 获取 ZIM 文件中特定条目的详细内容

**必需参数:**
- `zimFilePath` (字符串): ZIM 文件的路径
- `entryPath` (字符串): 条目路径，例如 'A/Some_Article'

**可选参数:**
- `maxContentLength` (整数, 默认值: 100000): 返回内容的最大长度

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


## License

MIT
