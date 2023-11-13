import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import serial
import psutil

# <<< GLOBAL variables
serial_obj = None
HOST = '0.0.0.0'
PORT = 13927
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
    if serial_obj and serial_obj.is_open:
        response = {"success": True,
                    "port": serial_obj.port,
                    "message": "There is a connection to the port '" + serial_obj.port + "'."}
    else:
        response = {"success": False,
                    "message": "There is no connection to any port."}
    return response

@app.get("/data")
async def get_data(reset: int=1):
    if serial_obj and serial_obj.is_open:
        response = {"success": True,
                    "data" : readline(reset==1)}
    else:
        response = {"success": False,
                    "message" : "There is no connection  to any port."}
    return response

@app.get("/connect")
async def connect(port: str=""):
    global serial_obj
    if port=="":
        return {"success": False,
                "message": "Please, specify 'port' number."}
    
    if serial_obj and serial_obj.is_open and serial_obj.port=="COM"+port:
        return {"success": True,
                "port" : serial_obj.port,
                "message": "The port '" + serial_obj.port + "' is already open."}
    close_port()
    
    result = connect_to_port(port)
    if result.get("success"):
        serial_obj = result.get("serial_object")
        response = {"success": True,
                    "port": serial_obj.port}
    else:
        response = {"success": False,
                    "error": result.get("error")}
    return response

@app.get("/close")
async def close():
    if close_port():
        response = {"success": True,
                "port": serial_obj.port,
                "message": "The connection has been closed."}
    else:
        response = {"success": True,
                "message": "There is no connection to any port."}    
    return response

# >>> API

# ---------------------------------------------------------

# <<< helper functions
def connect_to_port(port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1):
    port = 'COM' + str(port)
    try:
        return {"success": True,
                "serial_object": serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout)} 
    except serial.SerialException as ex:
        return {"success": False,
                "error": "could not open port '" + port + "'"}

def close_port():
    if serial_obj and serial_obj.is_open:
        serial_obj.close() 
        return 1
    else:
        return 0
    
def readline(reset):
    if reset:
        serial_obj.reset_input_buffer()

    SOF = "02"
    EOF = "03"
    # FIND START OF FRAME
    while serial_obj.read().hex() != SOF:
        continue
    # RECORD UNTIL END OF FRAME
    data = bytes()
    while True:
        temp = serial_obj.read()
        if temp.hex() == EOF:
            break
        else:
            data += temp
    return data.decode("utf-8")

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
