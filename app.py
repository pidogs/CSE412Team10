from flask import Flask, render_template, jsonify, request
import dbHelper

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# returns the columns that this table can be sorted by
@app.route("/columns")
def getColumns(): 
    try:
        conn = dbHelper.getConnection()
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'Model';
        """)
        columns = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(columns)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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