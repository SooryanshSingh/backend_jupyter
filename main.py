from flask import Flask, render_template, request, jsonify 
import sys
import io
from io import StringIO
from models import NotebookSession, active_notebooks

app = Flask(__name__)
notebook_id = "test_notebook"
active_notebooks[notebook_id] = NotebookSession(notebook_id)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/notebook/<notebook_id>/run/", methods=["POST"])
def run_code(notebook_id):
    if notebook_id not in active_notebooks:
        return jsonify({"detail": "Notebook session not found"}), 404

    session = active_notebooks[notebook_id]
    data = request.get_json()

    if not data or "code" not in data:
        return jsonify({"detail": "No code provided"}), 400

    code = data["code"]
    
    try:
        compile(code, "<string>", "exec")
    except IndentationError as e:
        return jsonify({
            "output": f"Indentation error: {str(e)}"
        }), 400
    except SyntaxError as e:
        return jsonify({
            "output": f"Syntax error: {str(e)}"
        }), 400

    try:
        old_stdout = sys.stdout
        new_output = sys.stdout = StringIO()

        exec(code, session.execution_globals)

        sys.stdout = old_stdout
        output = new_output.getvalue()

        output = output.rstrip('\n')

        if not output:
            output = "No output generated."

        return jsonify({
            "output": output
        })
        
    except Exception as e:
        sys.stdout = old_stdout
        output = f"Error: {str(e)}"
        return jsonify({
            "output": output
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
