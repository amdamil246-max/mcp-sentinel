"""
Mock MCP Terminal Server
Simulates an upstream MCP server exposing shell and command execution capabilities.
"""
import sys
import json

TOOLS = [
    {
        "name": "run_command",
        "description": "Executes a shell command inside the system environment.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The command string to execute"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "get_system_status",
        "description": "Retrieves real-time system performance, CPU, memory, and firewall metrics.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "search_logs",
        "description": "Queries historical system log messages with a keyword filter.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keyword to search in system logs"}
            },
            "required": ["query"]
        }
    }
]

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--list-tools":
        print(json.dumps(TOOLS, indent=2))
        return

    print("Mock MCP Terminal Server running on stdio.", file=sys.stderr)

if __name__ == "__main__":
    main()
