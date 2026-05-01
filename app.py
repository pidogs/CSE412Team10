from flask import Flask, render_template, jsonify, request, Response
import dbHelper
from psycopg2 import sql
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
    table_search_column = {
        "Model": "VariantName",
        "Aircraft": "Name",
        "Manufacturer": "Name",
    }
    user_table = request.args.get("scope")
    user_search = request.args.get("search")
    user_sort_col = request.args.get("sort_col")
    user_sort_dir = request.args.get("sort_dir")
    if user_table is None:
        return Response("Missing Table Scope", 400)
    if user_table not in table_search_column:
        return Response("Unrecognized or Disallowed Table", 404)
    conn = dbHelper.getConnection()
    cur = conn.cursor()

    if user_sort_col == "" or user_sort_col == None: # Don't want sorting
        cur.execute(sql.SQL("""
            SELECT * 
            FROM {}
            WHERE {} LIKE %s;
            ;
        """).format(sql.Identifier(user_table), sql.Identifier(table_search_column[user_table])),
        (f"%{user_search}%",))
    else:
        # We have f-string here but it is being used just to specify
        # DESC or ASC (after our own processing) so it should be safe
        # Actual user input is still being formatted using psycopg2
        sort_dir = "DESC" if user_sort_dir == "DESC" else "ASC"
        cur.execute(sql.SQL(f"""
            SELECT * 
            FROM {{}}
            WHERE {{}} LIKE %s
            ORDER BY {{}} {sort_dir};
        """).format(sql.Identifier(user_table), sql.Identifier(table_search_column[user_table]), sql.Identifier(user_sort_col)),
        (f"%{user_search}%",))
    result = {
        "description": [col.name for col in cur.description],
        "data": cur.fetchall()
    }
    print(result)
    return jsonify(result)
# End Justin's section

if __name__ == "__main__":
    app.run(debug=True)