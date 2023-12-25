import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil

# <<< GLOBAL variables
HOST = '0.0.0.0'
PORT = 8000
# >>> GLOBAL variables

# <<< API
app = FastAPI()

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {"status": "ok"}

def run_server():
    uvicorn.run(app=app, host=HOST, port=PORT, log_config=None)

def stop_server():
    for process in psutil.process_iter():
        connections =  process.connections()
        if len(connections) > 0:
            for conn in connections:
                if conn.laddr.ip == HOST and conn.laddr.port == PORT:
                    process.kill()
                    break
# >>> helper functions
