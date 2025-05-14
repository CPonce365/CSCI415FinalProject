from fastapi import FastAPI
import socket
import platform

app = FastAPI(title="Cdn node metrics")

@app.get("/")
async def root():
    """Root endpoint returns a simple hello world message"""
    return {
        "message": "Hello World from CDN Node!",
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "platform": platform.platform()
    }
@app.get("/metrics")
async def metrics():
    """Return system metrics for this CDN node"""
    import psutil
    connections = psutil.net_connections(kind='tcp')
    http_connections = [conn for conn in connections if conn.laddr.port == 80 and conn.status == 'ESTABLISHED']
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "connections": len(http_connections),
    }
@app.get("/health")
async def health_check():
    """Health check endpoint for the CDN node"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
