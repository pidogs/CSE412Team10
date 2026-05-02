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
        "Model": ["AircraftName", "VariantName"],
        "Aircraft": ["Name"],
        "Manufacturer": ["Name"],
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

    sort_dir_sql = "DESC" if user_sort_dir == "DESC" else "ASC"

    if user_table == "Manufacturer":
        order_clause = sql.SQL("")
        if user_sort_col is not None and user_sort_col != "":
            if user_sort_col == "ModelCount":
                order_clause = (
                    sql.SQL(" ORDER BY COALESCE(mm_cnt.cnt, 0) ")
                    + sql.SQL(sort_dir_sql)
                )
            elif user_sort_col in ("Name", "YearFounded"):
                order_clause = (
                    sql.SQL(" ORDER BY {} ").format(sql.Identifier(user_sort_col))
                    + sql.SQL(sort_dir_sql)
                )
        manufacturer_sql = sql.SQL("""
            SELECT m."Name", m."YearFounded",
                   COALESCE(mm_cnt.cnt, 0)::int AS "ModelCount"
            FROM "Manufacturer" m
            LEFT JOIN (
                SELECT "ManufacturerName", COUNT(*) AS cnt
                FROM "ModelManufacturer"
                GROUP BY "ManufacturerName"
            ) mm_cnt ON mm_cnt."ManufacturerName" = m."Name"
            WHERE m."Name" LIKE %s
        """) + order_clause
        cur.execute(manufacturer_sql, (f"%{user_search}%",))
    else:
        if user_table == "Model":
            query_raw = '''
                SELECT * 
                FROM "Model"
                LEFT JOIN "ModelManufacturer" ON "Model"."AircraftName" = "ModelManufacturer"."ModelAircraftName" AND "Model"."VariantName" = "ModelManufacturer"."ModelVariantName"
                LEFT JOIN "ModelEngineUsage" ON "Model"."AircraftName" = "ModelEngineUsage"."ModelAircraftName" AND "Model"."VariantName" = "ModelEngineUsage"."ModelVariantName"
                LEFT JOIN "EngineType" ON "ModelEngineUsage"."EngineModelName" = "EngineType"."ModelName"
                LEFT JOIN "ModelSeating" ON "Model"."AircraftName" = "ModelSeating"."ModelAircraftName" AND "Model"."VariantName" = "ModelSeating"."ModelVariantName"
                LEFT JOIN "SeatingArrangement" ON "ModelSeating"."SeatingID" = "SeatingArrangement"."ID"
                LEFT JOIN "SpeedRecord" ON "Model"."AircraftName" = "SpeedRecord"."ModelAircraftName" AND "Model"."VariantName" = "SpeedRecord"."ModelVariantName"
            '''
        else:
            query_raw =  '''SELECT * 
                FROM "Aircraft"'''
            
        if search_columns := table_search_column[user_table]:
            query_raw += "\nWHERE"
            query_raw += " OR ".join(["\n{} ILIKE %s" for _ in search_columns])
        
        if user_sort_col == "" or user_sort_col == None:
            query_raw += ";"
            identifiers = [sql.Identifier(user_table, search_col) for search_col in table_search_column[user_table]]
        else:
            query_raw += f"\nORDER BY {{}} {sort_dir_sql};"
            identifiers = [sql.Identifier(user_table, search_col) for search_col in table_search_column[user_table]] + \
                [sql.Identifier(user_table, user_sort_col)]
            
        cur.execute(sql.SQL(query_raw).format(
            *identifiers
        ), tuple([f"%{user_search}%" for search_col in table_search_column[user_table]]))
    result = {
        "description": [col.name for col in cur.description],
        "data": cur.fetchall()
    }
    return jsonify(result)
# End Justin's section


@app.route("/manufacturer-models")
def manufacturer_models():
    name = request.args.get("name")
    if not name or not name.strip():
        return jsonify({"error": "Missing manufacturer name"}), 400
    conn = dbHelper.getConnection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT m."AircraftName", m."VariantName", m."Range",
                   mm."Country", mm."YearEnd"
            FROM "ModelManufacturer" mm
            INNER JOIN "Model" m
              ON m."AircraftName" = mm."ModelAircraftName"
             AND m."VariantName" = mm."ModelVariantName"
            WHERE mm."ManufacturerName" = %s
            ORDER BY m."AircraftName", m."VariantName";
            """,
            (name.strip(),),
        )
        result = {
            "description": [col.name for col in cur.description],
            "data": cur.fetchall(),
        }
        return jsonify(result)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)