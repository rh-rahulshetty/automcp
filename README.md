# Auto-MCP

Turn any CLI or executable into MCP server.




```

source .venv/bin/activate
mkdir -p tmp
cd tmp

uv run automcp create -p "sqlite3" -o ./tmp/server.py

uv run automcp create -p "podman pull" -o ./tmp/server.py
```
