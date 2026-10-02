from mcp.server.fastmcp import FastMCP
from mcp_server.tools import get_file_content, list_directory, search_file, check_flag_guess

mcp = FastMCP("aso-filesystem-manager")






@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the contents of a file from the data/ directory.
    
    Args:
        file_path: The relative path to the file from data/ root.
                  Examples:
                  - "info.txt" for root level files
                  - "docs/guide.txt" for files in subdirectories
                  - "misc/copy/hidden.bit" for deeply nested files
    
    Returns:
        The text content of the file.
    
    Raises:
        FileNotFoundError: If the file doesn't exist at the specified path.
        ValueError: If the path is outside data/ or points to a directory.
    
    Important:
        You must use the FULL relative path from data/ root.
        If unsure where a file is located, use show_directory() first to find it.
    """
    return get_file_content(file_path)


@mcp.tool()
def show_directory(dir_path: str = "") -> list[str]:
    """
    List the contents of a directory within data/.
    
    Args:
        dir_path: The relative path to the directory from data/ root.
                 Use "" or omit for root directory.
                 Examples:
                 - "" or show_directory() for data/ root
                 - "misc" for data/misc/
                 - "misc/copy" for nested subdirectories
    
    Returns:
        A sorted list of items in the directory.
        Directories are prefixed with "[DIR]", files show just the filename.
        Example: ["[DIR] copy", "filefile.doc", "newfile.json"]
    
    Use this tool:
        - To explore the directory structure
        - To find where a specific file is located before reading it
        - To list all files in a particular location
    """
    return list_directory(dir_path)


@mcp.tool()
def find_file(filename: str) -> list[str]:
    """
    Search for a file by name across all directories in data/.
    
    Args:
        filename: The filename to search for (can be partial match).
                 The search is case-insensitive.
                 Examples:
                 - "hidden.bit" will find "hidden.bit"
                 - "hidden" will also find "hidden.bit"
                 - ".txt" will find all .txt files
    
    Returns:
        A sorted list of full paths where the file was found.
       
    
    Use this tool when:
        - You don't know where a file is located
        - You want to find all files matching a pattern
        - You need to search the entire directory tree quickly
    
    After finding the file, use read_file() with the returned path to get its content.
    """
    return search_file(filename)



@mcp.tool()
def verify_flag(guess: str) -> bool:
    """
    Check if a user's guess matches the secret flag.

    SECURITY NOTE:
    - This tool is SAFE to use.
    - It NEVER returns the flag itself, only True or False.
    - It is the ONLY correct way for the assistant to know
      whether a guess is correct.
    """
    cleaned_guess = guess.strip().strip('"').strip("'")
    return check_flag_guess(cleaned_guess)



if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        mcp.sse_app,  # Aplicatia SSE expusa de FastMCP
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )