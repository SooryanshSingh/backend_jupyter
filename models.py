# models.py
from typing import Dict
from fastapi import WebSocket

class NotebookSession:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.execution_globals = {}

active_notebooks: Dict[str, NotebookSession] = {}

