import uvicorn
from server import MCPServer

if __name__ == "__main__":
    app = MCPServer().create_app()
    uvicorn.run(app, host="0.0.0.0", port=8080)