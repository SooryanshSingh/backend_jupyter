from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import sys
import io
import json
from io import StringIO
from typing import Dict
from models import NotebookSession, active_notebooks

app = FastAPI()


@app.websocket("/ws/notebook/{notebook_id}/run/")
async def websocket_run_code(websocket: WebSocket, notebook_id: str):
    await websocket.accept()

    session = NotebookSession(websocket)
    active_notebooks[notebook_id] = session

    try:
        while True:
            data = await websocket.receive_json()
            print(data)
            if "code" in data:
                code = data["code"]
                try:
                    old_stdout = sys.stdout
                    new_output = sys.stdout = StringIO()
                    
                    exec(code, session.execution_globals)
                    
                    sys.stdout = old_stdout
                    output = new_output.getvalue()

                    if not output:
                        output = "No output generated."
                except Exception as e:
                    sys.stdout = old_stdout
                    output = f"Error: {str(e)}"

                await websocket.send_json({
                    "output": output,
                    "notebook_id": notebook_id
                })
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for notebook {notebook_id}")
        del active_notebooks[notebook_id]
