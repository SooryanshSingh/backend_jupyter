from flask import Flask, render_template, request, jsonify
import sys
import io
from io import StringIO
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
print("Supabase URL:", os.getenv("SUPABASE_URL"))
print("Supabase API Key:", os.getenv("SUPABASE_API_KEY"))

supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/notebook/<notebook_id>/run/", methods=["POST"])
def run_code(notebook_id):
    response = supabase.table('notebooks').select('notebook_id', 'name').eq('notebook_id', notebook_id).execute()

    if not response.data:
        return jsonify({"detail": "Notebook not found"}), 404

    notebook = response.data[0]
    
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

        exec(code, {})

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
