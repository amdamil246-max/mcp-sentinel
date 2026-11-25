"""
Mock MCP Filesystem Server
Simulates an upstream MCP server exposing filesystem operations.
"""
import sys
import json

TOOLS = [
    {
        "name": "read_file",
        "description": "Reads raw contents of a target file from disk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute or relative file path to read"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Writes text or code content to a designated file path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Destination file path"},
                "content": {"type": "string", "description": "File contents"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_directory",
        "description": "Lists files and subdirectories within a given folder path.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Folder path to list"}
            },
            "required": ["path"]
        }
    }
]

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--list-tools":
        print(json.dumps(TOOLS, indent=2))
        return

    print("Mock MCP Filesystem Server running on stdio.", file=sys.stderr)

if __name__ == "__main__":
    main()
