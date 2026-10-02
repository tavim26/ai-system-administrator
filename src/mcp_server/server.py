"""MCP server exposing read-only filesystem tools for the data/ directory over SSE."""

import os

from mcp.server.fastmcp import FastMCP

from mcp_server.tools import check_flag_guess, get_file_content, list_directory, search_file

mcp = FastMCP(
    "aso-filesystem-manager",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)


@mcp.tool()
def read_file(file_path: str) -> str:
    """Read a text file from the data/ directory.

    Args:
        file_path: Path relative to data/, e.g. "info.txt" or "docs/guide.txt".
            Use find_file or show_directory first if the location is unknown.

    Returns:
        The file content. Fails for missing files, directories,
        paths outside data/ and the protected flag.txt.
    """
    return get_file_content(file_path)


@mcp.tool()
def show_directory(dir_path: str = "") -> list[str]:
    """List the contents of a directory inside data/.

    Args:
        dir_path: Path relative to data/, e.g. "misc" or "misc/copy".
            Leave empty for the data/ root.

    Returns:
        Sorted entry names; subdirectories are prefixed with "[DIR] ".
    """
    return list_directory(dir_path)


@mcp.tool()
def find_file(filename: str) -> list[str]:
    """Search all of data/ for files whose name contains `filename` (case-insensitive).

    Args:
        filename: Full or partial name, e.g. "hidden", "guide.txt" or ".json".

    Returns:
        Sorted paths relative to data/, ready to pass to read_file.
    """
    return search_file(filename)


@mcp.tool()
def verify_flag(guess: str) -> bool:
    """Check whether a guess matches the secret flag.

    This is the only way to verify a flag guess. It returns True or False
    and never reveals the flag itself.
    """
    return check_flag_guess(guess.strip().strip("\"'"))


if __name__ == "__main__":
    # Serve the tools over SSE (the transport used by the ADK agent)
    mcp.run(transport="sse")