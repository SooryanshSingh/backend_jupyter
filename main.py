from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sys
from io import StringIO
import os
from dotenv import load_dotenv
from supabase import create_client
import markdown

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")
app.debug = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Allows the session cookie to be sent across sites
app.config['SESSION_COOKIE_SECURE'] = False  # For development purposes, False means cookies will not require HTTPS

# Routes for authentication and navigation
@app.route("/")
def home():
        return redirect(url_for("homepage"))

@app.route("/signin", methods=["GET", "POST"])
def signin():

    return render_template("signin.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    
    return render_template("signup.html")

@app.route("/logout")
def logout():
    return redirect(url_for("homepage"))  # Redirect to sign-in page

@app.route("/homepage", methods=["GET"])
def homepage():
    if 'user' not in session:
        print("User is not logged in")
    else:
        print("User is logged in:", session['user'])
    return render_template("homepage.html")

@app.route("/code")
def code():
    return render_template("code.html")

@app.route("/notebook/<notebook_id>/cell/<cell_id>/run/", methods=["POST"])
def run_cell_code(notebook_id, cell_id):
    print(f"Received notebook_id: {notebook_id}, cell_id: {cell_id}")

    # Fetch cell data
    response = supabase.table('cells').select('cell_id', 'notebook_id', 'code').eq('cell_id', cell_id).eq('notebook_id', notebook_id).execute()

    if not response.data:
        return jsonify({"detail": "Cell not found"}), 404

    cell = response.data[0]

    # Get code from the request
    data = request.get_json()

    if not data or "code" not in data:
        return jsonify({"detail": "No code provided"}), 400

    code = data["code"]
    supabase.table('cells').update({"code": code}).eq("cell_id", cell_id).execute()

    try:
        # Validate the code syntax
        compile(code, "<string>", "exec")
    except IndentationError as e:
        return jsonify({"output": f"Indentation error: {str(e)}"}), 400
    except SyntaxError as e:
        return jsonify({"output": f"Syntax error: {str(e)}"}), 400

    try:
        old_stdout = sys.stdout
        new_output = sys.stdout = StringIO()

        exec(code, {})

        sys.stdout = old_stdout
        output = new_output.getvalue().strip()

        if not output:
            output = "No output generated."

        return jsonify({"output": output})

    except Exception as e:
        sys.stdout = old_stdout
        return jsonify({"output": f"Error: {str(e)}"}), 500

@app.route("/notebook/<notebook_id>/add_cell/", methods=["POST"])
def add_cell(notebook_id):
    try:
        new_cell = supabase.table("cells").insert({"notebook_id": notebook_id, "code": ""}).execute()

        if not new_cell.data:
            return jsonify({"detail": "Failed to create cell"}), 500

        return jsonify(new_cell.data[0]), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/notebook/<notebook_id>/cells/", methods=["GET"])
def get_cells(notebook_id):
    try:
        response = supabase.table("cells").select("*").eq("notebook_id", notebook_id).execute()

        if not response.data:
            return jsonify([]), 200

        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/notebook/<notebook_id>/cell/<cell_id>/delete/", methods=["DELETE"])
def delete_cell(notebook_id, cell_id):
    try:
        # Delete the cell from the database
        response = supabase.table("cells").delete().eq("notebook_id", notebook_id).eq("cell_id", cell_id).execute()

        if not response.data:
            return jsonify({"detail": "Cell not found or already deleted"}), 404

        return jsonify({"message": "Cell deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/notebook/add_mark/", methods=["POST"])
def add_markup():
    try:
        new_cell = supabase.table("markup").insert({"code": ""}).execute()

        if not new_cell.data:
            return jsonify({"detail": "Failed to create cell"}), 500

        return jsonify(new_cell.data[0]), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/notebook/markup/<cell_id>/delete/", methods=["DELETE"])
def delete_markup(cell_id):
    try:
        print("OK")
        response = supabase.table("markup").delete().eq("id", cell_id).execute()

        if response.data is None or len(response.data) == 0:
            return jsonify({"detail": "Cell not found or already deleted"}), 404

        return jsonify({"message": "Cell deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route("/notebook/markup/<cell_id>/run/", methods=["POST"])
def render_markdown(cell_id):
    try:
        data = request.get_json()
        markup_text = data.get("code", "")
        supabase.table('markup').update({"code": markup_text}).eq("id", cell_id).execute()
        html_output = markdown.markdown(markup_text)
        print("saved markup")
        return jsonify({"rendered_html": html_output}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/notebook/mark/", methods=["GET"])
def get_mark():
    try:
        response = supabase.table("markup").select("*").execute()

        if not response.data:
            return jsonify([]), 200

        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
