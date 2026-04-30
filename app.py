from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# Justin's section don't touch unless for very minor fixes
# Returns results of queries as JSON data.
@app.route("/data")
def handle_query():
    # Standard format:
    # {
    #   description: list[str] containing column names
    #   data: list[list[<query data result type>]] containing all rows of the output
    # }
    return jsonify({})
# End Justin's section

if __name__ == "__main__":
    app.run(debug=True)