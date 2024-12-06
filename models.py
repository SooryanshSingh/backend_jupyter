# models.py
from typing import Dict

class NotebookSession:
    def __init__(self,notebook_id):
        self.notebook_id = notebook_id
        self.execution_globals = {}

active_notebooks: Dict[str, NotebookSession] = {}
