from flask import Flask, render_template, request
from mcp_analyzer import MCPSystem
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
mcp = MCPSystem()

@app.route("/", methods=["GET", "POST"])
def index():
    response = ""
    code_output = ""
    source_url = ""
    query = ""
    feature = ""

    if request.method == "POST":
        source_url = request.form.get("source_url")
        query = request.form.get("query")
        feature = request.form.get("feature")

        if source_url:
            response = mcp.load_source(source_url)
        if query:
            response = mcp.process_query(query)
        if feature:
            code_output = mcp.generate_code(feature)

    return render_template("index.html",
                           response=response,
                           code_output=code_output,
                           source_url=source_url,
                           query=query,
                           feature=feature)

if __name__ == "__main__":
    app.run(debug=True)
