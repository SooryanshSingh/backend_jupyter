  const cellsContainer = document.getElementById("cellsContainer");
        const addCellButton = document.getElementById("addCell");

        const notebookId = "1";

        async function loadCells() {
            try {
                const response = await fetch(`/notebook/${notebookId}/cells/`);
                const cells = await response.json();

                cells.forEach(cell => {
                    renderCell(cell.cell_id, cell.code || "");
                });
            } catch (error) {
                console.error("Error loading cells:", error.message);
            }
        }

        function renderCell(cellId, code = "") {
            const cellDiv = document.createElement("div");
            cellDiv.id = `cell-${cellId}`;
            cellDiv.innerHTML = `
        <textarea id="code-${cellId}" class="note-content" rows="5" cols="50" 
        style="width: 100%; min-height: 100px; padding: 10px; resize: none; overflow: hidden;" 
        placeholder="Write your code here...">${code}</textarea>
        
                <button class="save-note" onclick="runCellCode(${notebookId}, ${cellId})">Run Code</button>
                <button class="delete-note" onclick="deleteCell(${notebookId}, ${cellId})">Delete Cell</button>
                <div class="output" id="output-${cellId}">Output will appear here...</div>
            `;
        
            cellsContainer.appendChild(cellDiv);
        }
        

        addCellButton.addEventListener("click", async () => {
            try {
                const response = await fetch(`/notebook/${notebookId}/add_cell/`, {
                    method: "POST"
                });

                const result = await response.json();
                
                if (!result.cell_id) {
                    throw new Error("Failed to get cell ID.");
                }
                const cellId = result.cell_id; 

                renderCell(cellId);

            } catch (error) {
                alert("Error adding cell: " + error.message);
            }
        });

        function runCellCode(notebookId, cellId) {
            const codeInput = document.getElementById(`code-${cellId}`);
            const outputDiv = document.getElementById(`output-${cellId}`);

            if (!codeInput || !outputDiv) {
                return;
            }

            const code = codeInput.value;

            const url = `/notebook/${notebookId}/cell/${cellId}/run/`;

            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ code }),
            })
            .then((response) => response.json())
            .then((data) => {
                outputDiv.innerText = data.output;
            })
            .catch((error) => {
                outputDiv.innerText = `Error: ${error.message}`;
            });
        }
        function deleteCell(notebookId, cellId) {
            const url = `/notebook/${notebookId}/cell/${cellId}/delete/`;
        
            fetch(url, {
                method: "DELETE",
            })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Failed to delete cell: ${response.statusText}`);
                }
                return response.json();
            })
            .then((data) => {
                alert(data.message || "Cell deleted successfully");
                // Remove the cell element from the DOM
                const cellDiv = document.getElementById(`cell-${cellId}`);
                if (cellDiv) {
                    cellDiv.remove();
                }
            })
            .catch((error) => {
                alert(`Error deleting cell: ${error.message}`);
            });
        }
        
        loadCells();
