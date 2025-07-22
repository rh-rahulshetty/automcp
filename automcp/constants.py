OUTPUT_TEMPLATE = '''
MCP server created at {server_path}

Add following MCP server configuration to mcp.json:
{{
    "mcpServers": {{
        "{safe_command_name}": {{
            "command": "uv",
            "args": [
                "--directory",
                "{save_dir}",
                "run",
                "{output_file_name}"
            ]
        }}
    }}
}}

To automatically register this server to an MCP Gateway, set the environment variables 
MCP_GATEWAY_URL (e.g., http://localhost:4444), MCP_SERVER_URL (e.g., http://localhost:8000/sse),
and optionally MCP_GATEWAY_TOKEN (Bearer token for authentication) when running the server.

Run 'automcp gateway' to start a local MCP Gateway.
'''
