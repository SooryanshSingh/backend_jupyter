const supabaseurl = window.config.SUPABASE_URL;
const supabasekey = window.config.SUPABASE_KEY;

const supabaseclient = supabase.createClient(supabaseurl, supabasekey);

async function checkUser() {
  try {
   
    const { data: { user }, error: userError } = await supabaseclient.auth.getUser();


    if (user) {
      console.log("User is logged in:", user);
    } else {
      console.log("No user is logged in");
      window.location.href = '/signin'; 
    }
  } catch (err) {
    console.error("Unexpected error:", err.message);
  }
}





 
 const cellsContainer = document.getElementById("cellsContainer");
        const addCellButton = document.getElementById("addCell");
  const mark= document.getElementById("addMark");
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
        async function loadMark() {
            try {
                const response = await fetch(`/notebook/mark`);
                const cells = await response.json();

                cells.forEach(cell => {
                    renderM(cell.cell_id, cell.code || "");
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
        function renderM(cellId, code = "") {
            const cellDiv = document.createElement("div");
            cellDiv.id = `cell-${cellId}`;
            cellDiv.innerHTML = `
        <textarea id="code-${cellId}" class="note-content" rows="5" cols="50" 
        style="width: 100%; min-height: 100px; padding: 10px; resize: none; overflow: hidden;" 
        placeholder="Write your markup here...">${code}</textarea>
        
                <button class="save-note" onclick="runMark(${cellId})">Run Markup</button>
                <button class="delete-note" onclick="deleteMark(${cellId})">Delete Cell</button>
                <div class="output" id="outputm-${cellId}">Output will appear here...</div>
            `;
        
            cellsContainer.appendChild(cellDiv);
        }
        


        mark.addEventListener("click", async () => {
            try {
                const response = await fetch(`/notebook/add_mark/`, {
                    method: "POST"
                });

                const result = await response.json();
                
                if (!result.id) {
                    throw new Error("Failed to get cell ID.");
                }
                const cellId = result.id; 

                renderM(cellId);

            } catch (error) {
                alert("Error adding cell: " + error.message);
            }
        });
        function deleteMark(cell_id) {
            const url = `/notebook/markup/${cell_id}/delete/`;
            console.log(url);
        
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
                const cellDiv = document.getElementById(`cell-${cell_id}`);
                if (cellDiv) {
                    cellDiv.remove();
                }
            })
            .catch((error) => {
                alert(`Error deleting cell: ${error.message}`);
            });
        }
        function runMark (cellId) {
            const codeInput = document.getElementById(`code-${cellId}`);
            const outputDiv = document.getElementById(`outputm-${cellId}`);
        
            if (!codeInput || !outputDiv) {
                return;
            }
        
            const code = codeInput.value;
        
            // Construct the URL to the Flask route with the cellId
            const url = `/notebook/markup/${cellId}/run/`;
        
            // Send the Markdown content to the server
            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ code: code }), // Send the code in the request body
            })
            .then((response) => {
                // Log the raw response to the console
                console.log("Response Status:", response.status);
                return response.text(); // Get the response as text
            })
            .then((text) => {
                console.log("Raw response body:", text); // Log the raw response body
                try {
                    const data = JSON.parse(text); // Parse the response as JSON
                    if (data.rendered_html) {
                        // Insert the rendered HTML into the output div
                        outputDiv.innerHTML = data.rendered_html;
                    } else {
                        // Handle errors if no rendered HTML is returned
                        outputDiv.innerText = "Error: No rendered HTML returned.";
                    }
                } catch (error) {
                    // If JSON parsing fails, log the error
                    console.error("JSON parsing error:", error);
                    outputDiv.innerText = `Error: Unable to parse response as JSON.`;
                }
            })
            .catch((error) => {
                // Handle any errors that occurred during the fetch operation
                console.error("Fetch error:", error);
                outputDiv.innerText = `Error: ${error.message}`;
            });
        }
        checkUser();
                        
        loadCells();
        loadMark();
