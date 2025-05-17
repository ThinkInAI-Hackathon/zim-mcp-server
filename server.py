import json
import os
import re
import sys
import html2text
from datetime import datetime
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
from libzim.reader import Archive
from libzim.search import Query, Searcher
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("zim-mcp-server")
path_manager = None


class PathManager:
    """Manage file path access permissions"""

    def __init__(self, allowed_directories: List[str]):
        """
        Initialize path manager

        Args:
            allowed_directories: List of directories allowed for access
        """
        self.allowed_directories = [
            Path(self._normalize_path(d)).resolve() for d in allowed_directories]

        # Check if all directories exist
        for dir_path in self.allowed_directories:
            if not dir_path.is_dir():
                raise ValueError(f"Error: {dir_path} is not a directory")

    def _normalize_path(self, filepath: str) -> str:
        """
        Normalize path, expand home directory (~)

        Args:
            filepath: Path to normalize

        Returns:
            Normalized path string
        """
        # Expand home directory (~)
        if filepath.startswith('~'):
            filepath = os.path.expanduser(filepath)
        return os.path.normpath(filepath)

    def validate_path(self, requested_path: str) -> str:
        """
        Validate if the requested path is within allowed directories

        Args:
            requested_path: Path requested for access

        Returns:
            Validated absolute path

        Raises:
            ValueError: When path is outside allowed directories
        """
        expanded_path = self._normalize_path(requested_path)
        abs_path = Path(expanded_path).resolve()

        # Check if path is within allowed directories
        is_allowed = any(str(abs_path).startswith(str(allowed_dir))
                         for allowed_dir in self.allowed_directories)

        if not is_allowed:
            allowed_dirs_str = ', '.join(str(d)
                                         for d in self.allowed_directories)
            raise ValueError(
                f"Access denied - Path is outside allowed directories: {abs_path} is not in {allowed_dirs_str}")

        return str(abs_path)


def html_to_plain_text(html: str) -> str:
    """
    Convert HTML to plain text using bs4 and html2text

    Args:
        html: HTML content

    Returns:
        Converted plain text
    """
    # Use BeautifulSoup to clean HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Remove unwanted elements
    for element in soup.select('script, style, meta, link, head, footer, .mw-parser-output .reflist, .mw-editsection'):
        element.decompose()

    # Use html2text to convert HTML to Markdown format text
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_tables = False
    h.unicode_snob = True  # Use Unicode instead of ASCII
    h.body_width = 0  # No line wrapping

    text = h.handle(str(soup))

    # Clean up excess empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


@mcp.tool()
async def list_zim_files() -> str:
    """List all ZIM files in allowed directories

    Returns:
        JSON string containing the list of ZIM files
    """
    if not path_manager:
        return "Error: Directory permission manager not initialized"

    all_zim_files = []

    for directory in path_manager.allowed_directories:
        try:
            for file_path in directory.glob('**/*.zim'):
                if file_path.is_file():
                    stats = file_path.stat()
                    all_zim_files.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "directory": str(directory),
                        "size": f"{stats.st_size / (1024 * 1024):.2f} MB",
                        "modified": datetime.fromtimestamp(stats.st_mtime).isoformat()
                    })
        except Exception as e:
            print(
                f"Error processing directory {directory}: {str(e)}", file=sys.stderr)

    if not all_zim_files:
        return "No ZIM files found in allowed directories"

    result_text = f"Found {len(all_zim_files)} ZIM files in {len(path_manager.allowed_directories)} directories:\n\n"
    result_text += json.dumps(all_zim_files, indent=2, ensure_ascii=False)
    return result_text


@mcp.tool()
async def search_zim_file(zimFilePath: str, query: str, limit: int = 10, offset: int = 0) -> str:
    """Search within ZIM file content

    Args:
        zimFilePath: Path to the ZIM file
        query: Search query term
        limit: Maximum number of results to return
        offset: Result starting offset (for pagination)

    Returns:
        Search result text
    """
    try:
        if path_manager:
            valid_path = path_manager.validate_path(zimFilePath)
        else:
            valid_path = zimFilePath
            if not os.path.exists(valid_path):
                return f"Error: ZIM file not found: {valid_path}"

        # Validate file exists and is a ZIM file
        valid_path_obj = Path(valid_path)
        if not valid_path_obj.is_file():
            return "Error: Specified path is not a file"
        if not valid_path_obj.suffix.lower() == '.zim':
            return "Error: Specified file is not a ZIM file"

        # Open ZIM archive
        archive = Archive(valid_path)
        print(f"Archive opened: {valid_path}", file=sys.stderr)

        # Create searcher and execute search
        query_obj = Query().set_query(query)
        searcher = Searcher(archive)
        search = searcher.search(query_obj)

        # Get total results
        total_results = search.getEstimatedMatches()

        if total_results == 0:
            return f'No search results found for "{query}"'

        result_count = min(limit, total_results - offset)

        # Get search results
        result_entries = list(search.getResults(offset, result_count))

        # Collect search results
        results = []
        for i, entry_id in enumerate(result_entries):
            try:
                # Get entry object
                entry = archive.get_entry_by_path(entry_id)
                title = entry.title or "Untitled"

                # Get content snippet
                try:
                    item = entry.get_item()
                    if item.mimetype.startswith('text/'):
                        raw_content = bytes(item.content).decode(
                            'utf-8', errors='replace')
                        if item.mimetype.startswith('text/html'):
                            # Use the new html_to_plain_text function
                            content_text = html_to_plain_text(raw_content)
                            # Extract first few paragraphs as snippet
                            paragraphs = content_text.split('\n\n')
                            if paragraphs:
                                snippet = ' '.join(
                                    # Take only first two paragraphs to keep it concise
                                    paragraphs[:2])
                            else:
                                snippet = content_text
                        else:
                            snippet = raw_content

                        # Limit length
                        snippet = snippet[:500].strip(
                        ) + "..." if len(snippet) > 500 else snippet
                    else:
                        snippet = f"(Unsupported content type: {item.mimetype})"
                except Exception as e:
                    print(
                        f"Error getting content for entry {entry_id}: {str(e)}", file=sys.stderr)
                    snippet = "(Unable to get content preview)"

                results.append({
                    "path": entry_id,
                    "title": title,
                    "snippet": snippet
                })
            except Exception as e:
                print(
                    f"Error getting entry {entry_id}: {str(e)}", file=sys.stderr)
                results.append({
                    "path": entry_id,
                    "title": f"Entry {offset + i + 1}",
                    "snippet": f"(Error getting entry details: {str(e)})"
                })

        # Build result text
        result_text = f'Found {total_results} matches for "{query}", showing {offset + 1}-{offset + len(results)}:\n\n'

        for i, result in enumerate(results):
            result_text += f"## {offset + i + 1}. {result['title']}\n"
            result_text += f"Path: {result['path']}\n"
            result_text += f"Snippet: {result['snippet']}\n\n"

        return result_text

    except Exception as e:
        print(f"Error searching ZIM file: {str(e)}", file=sys.stderr)
        return f"Error: Failed to search ZIM file: {str(e)}"


@mcp.tool()
async def get_zim_entry(zimFilePath: str, entryPath: str, maxContentLength: int = 100000) -> str:
    """Get detailed content of a specific entry in a ZIM file

    Args:
        zimFilePath: Path to the ZIM file
        entryPath: Entry path, e.g., 'A/Some_Article'
        maxContentLength: Maximum length of content to return

    Returns:
        Entry content text
    """
    try:
        # Validate file path
        if path_manager:
            valid_path = path_manager.validate_path(zimFilePath)
        else:
            valid_path = zimFilePath
            if not os.path.exists(valid_path):
                return f"Error: ZIM file not found: {valid_path}"

        # Validate file exists and is a ZIM file
        valid_path_obj = Path(valid_path)
        if not valid_path_obj.is_file():
            return "Error: Specified path is not a file"
        if not valid_path_obj.suffix.lower() == '.zim':
            return "Error: Specified file is not a ZIM file"

        # Open ZIM archive
        archive = Archive(valid_path)
        print(
            f"Archive opened: {valid_path}, attempting to get entry: {entryPath}", file=sys.stderr)

        # Get specified entry
        try:
            entry = archive.get_entry_by_path(entryPath)

            # Get entry title
            title = entry.title or "Untitled"
            print(f"Entry found: {title}, path: {entryPath}", file=sys.stderr)

            # Get content
            content = ""
            content_type = ""

            try:
                item = entry.get_item()
                mime_type = item.mimetype or ""
                content_type = mime_type
                print(f"Entry MIME type: {mime_type}", file=sys.stderr)

                # Get data
                if mime_type.startswith('text/html'):
                    # Process HTML content
                    raw_content = bytes(item.content).decode(
                        'utf-8', errors='replace')

                    # Convert HTML to plain text
                    content = html_to_plain_text(raw_content)

                elif mime_type.startswith('text/'):
                    # Process other text
                    content = bytes(item.content).decode(
                        'utf-8', errors='replace')
                elif mime_type.startswith('image/'):
                    content = '(Image content - Cannot display directly)'
                else:
                    content = f'(Unsupported content type: {mime_type})'

            except Exception as e:
                print(
                    f"Error getting entry content: {str(e)}", file=sys.stderr)
                content = f"(Error retrieving content: {str(e)})"

        except Exception as e:
            print(f"Error getting ZIM entry: {str(e)}", file=sys.stderr)
            return f"Error: Failed to get ZIM entry: {str(e)}"

        # Limit content length to avoid exceeding token limits
        if content and len(content) > maxContentLength:
            truncated_content = content[:maxContentLength]
            content = truncated_content + \
                f"\n\n... [Content truncated, total of {len(content)} characters, only showing first {maxContentLength} characters] ..."

        # Build return content
        result_text = f"# {title}\n\n"
        result_text += f"Path: {entryPath}\n"
        result_text += f"Type: {content_type or 'Unknown'}\n"
        result_text += f"## Content\n\n"
        result_text += content or "(No content)"

        return result_text

    except Exception as e:
        print(f"Error processing ZIM file: {str(e)}", file=sys.stderr)
        return f"Error: Failed to process ZIM file: {str(e)}"


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(
            "Usage: uv run server.py <allowed_directory> [other_directories...]", file=sys.stderr)
        sys.exit(1)

    try:
        path_manager = PathManager(args)
        print(
            f"ZIM MCP server started, allowed directories: {', '.join(args)}", file=sys.stderr)

        mcp.run(transport='stdio')
    except Exception as e:
        print(f"Server startup error: {str(e)}", file=sys.stderr)
        sys.exit(1)
