from flask import Flask, render_template, request, jsonify
import sys
from io import StringIO
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

app = Flask(__name__)
app.degug=True
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/notebook/<notebook_id>/cell/<cell_id>/run/", methods=["POST"])
def run_cell_code(notebook_id, cell_id):
    print(f"Received notebook_id: {notebook_id}, cell_id: {cell_id}")  # Log received values

    # Fetch cell data
    response = supabase.table('cells').select('cell_id', 'notebook_id', 'code').eq('cell_id', cell_id).eq('notebook_id', notebook_id).execute()

    print(f"Response from supabase: {response}")  # Log the response data from supabase

    if not response.data:
        print("Cell not found!")
        return jsonify({"detail": "Cell not found"}), 404

    cell = response.data[0]
    print(f"Cell data: {cell}")  # Log the cell data

    # Get code from the request
    data = request.get_json()
    print(f"Received data: {data}")  # Log the data received in the request

    if not data or "code" not in data:
        print("No code provided!")
        return jsonify({"detail": "No code provided"}), 400

    code = data["code"]

    try:
        # Validate the code syntax
        compile(code, "<string>", "exec")
    except IndentationError as e:
        print(f"Indentation error: {str(e)}")
        return jsonify({"output": f"Indentation error: {str(e)}"}), 400
    except SyntaxError as e:
        print(f"Syntax error: {str(e)}")
        return jsonify({"output": f"Syntax error: {str(e)}"}), 400

    try:
        # Capture stdout to get the code output
        old_stdout = sys.stdout
        new_output = sys.stdout = StringIO()

        exec(code, {})

        # Restore stdout and fetch the output
        sys.stdout = old_stdout
        output = new_output.getvalue().strip()

        if not output:
            output = "No output generated."

        print(f"Output from execution: {output}")  # Log the output

        return jsonify({"output": output})

    except Exception as e:
        # Restore stdout and log the exception
        sys.stdout = old_stdout
        print(f"Error while executing code: {str(e)}")
        return jsonify({"output": f"Error: {str(e)}"}), 500


@app.route("/notebook/<notebook_id>/add_cell/", methods=["POST"])
def add_cell(notebook_id):
    try:
        # Insert a new cell into the database
        new_cell = supabase.table("cells").insert({"notebook_id": notebook_id, "code": ""}).execute()

        # Debugging: log the new cell data
        print("New cell response:", new_cell)

        if not new_cell.data:
            return jsonify({"detail": "Failed to create cell"}), 500

        # Ensure we're returning the correct 'id' from the inserted cell
        return jsonify(new_cell.data[0]), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

   


@app.route("/notebook/<notebook_id>/cells/", methods=["GET"])
def get_cells(notebook_id):
    try:
        # Fetch all cells for a specific notebook
        response = supabase.table("cells").select("*").eq("notebook_id", notebook_id).execute()

        if not response.data:
            return jsonify([]), 200

        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

