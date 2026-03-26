import csv
import os
import psycopg2

CSV_DIR = "CSV"

# Database connection parameters from your Nix environment
DB_NAME = "aircraft_db"
DB_USER = "aircraft_db"

DB_HOST = os.environ.get("PGHOST", "127.0.0.1")
DB_PORT = os.environ.get("PGPORT", "5432")


def getConnection():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT,password=""
    )


def resetDatabase():
    print("Connecting to database")
    conn = getConnection()
    conn.autocommit = True
    cursor = conn.cursor()

    # All tables to drop
    tables = [
        "SpeedRecord",
        "Model_Seating",
        "Model_Manufacturer",
        "Model_Engine_Usage",
        "Model",
        "SeatingArrangement",
        "EngineType",
        "FuelType",
        "Manufacturer",
        "Aircraft",
    ]

    # Droping tables
    print("Dropping tables")
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')

    # Make table structs 
    print("Creating tables")
    schema = """
    CREATE TABLE "Aircraft" (
        "Name" VARCHAR(255) PRIMARY KEY
    );

    CREATE TABLE "Manufacturer" (
        "Name" VARCHAR(255) PRIMARY KEY,
        "YearFounded" INT
    );

    CREATE TABLE "FuelType" (
        "Name" VARCHAR(255),
        "Octane" INT,
        "Energy_MJ_kg" FLOAT,
        "Weight_lb_gal" FLOAT,
        "Leaded" BOOLEAN,
        "Color" VARCHAR(50),
        PRIMARY KEY("Name", "Octane")
    );

    CREATE TABLE "EngineType" (
        "ModelName" VARCHAR(255) PRIMARY KEY,
        "Thrust" FLOAT,
        "CylinderCount" FLOAT,
        "CylinderConfig" VARCHAR(100),
        "PropSize" FLOAT
    );

    CREATE TABLE "SeatingArrangement" (
        "ID" INT PRIMARY KEY,
        "FirstClassCount" INT,
        "BusinessClassCount" INT,
        "EconomyCount" INT,
        "PilotCount" INT,
        "OtherCount" INT
    );

    CREATE TABLE "Model" (
        "VariantName" VARCHAR(255) PRIMARY KEY,
        "AircraftName" VARCHAR(255) REFERENCES "Aircraft"("Name"),
        "Range" FLOAT,
    );

    CREATE TABLE "Model_Engine_Usage" (
        "ModelVariantName" VARCHAR(255) REFERENCES "Model"("VariantName"),
        "EngineModelName" VARCHAR(255),
        "NumberOfEngines" INT
    );

    CREATE TABLE "Model_Manufacturer" (
        "ModelVariantName" VARCHAR(255) REFERENCES "Model"("VariantName"),
        "ManufacturerName" VARCHAR(255) REFERENCES "Manufacturer"("Name"),
        "Country" VARCHAR(255),
        "YearEnd" INT
    );

    CREATE TABLE "Model_Seating" (
        "ModelVariantName" VARCHAR(255) REFERENCES "Model"("VariantName"),
        "SeatingID" INT REFERENCES "SeatingArrangement"("ID")
    );

    CREATE TABLE "SpeedRecord" (
        "RecordID" INT PRIMARY KEY,
        "ReportedModel" VARCHAR(255),
        "ModelVariantName" VARCHAR(255),
        "DateSet" DATE,
        "SpeedKph" FLOAT,
        "Sponsor" VARCHAR(255),
        "Description" TEXT
    );
    """
    cursor.execute(schema)
    cursor.close()
    conn.close()
    print("Tables created successfully")


def loadCSV(file_path, table_name, columns):
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} not found")
        return

    print(f"Loading data into {table_name} from {file_path}")
    conn = getConnection()
    cursor = conn.cursor()

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # unused
        
        # Prepare insert query with quoted column names
        quoted_cols = [f'"{col}"' for col in columns]
        cols = ", ".join(quoted_cols)
        placeholders = ", ".join(["%s"] * len(columns))
        query = f'INSERT INTO "{table_name}" ({cols}) VALUES ({placeholders})'

        for row in reader:
            # Replace empty strings with None so database will use NULLs
            cleanRow = [val if val.strip() != "" else None for val in row]
            
            # if missing rows then pad rows
            while len(cleanRow) < len(columns):
                cleanRow.append(None)
                
            cursor.execute(query, cleanRow[:len(columns)])

    conn.commit()
    cursor.close()
    conn.close()


def main():
    print("RESET DB")
    resetDatabase()
    
    # Parents
    loadCSV(f"{CSV_DIR}/Aircraft.csv", "Aircraft", ["Name"])
    loadCSV(f"{CSV_DIR}/Manufacturer.csv", "Manufacturer", ["Name", "YearFounded"])
    loadCSV(
        f"{CSV_DIR}/FuelType.csv", 
        "FuelType", 
        ["Name", "Octane", "Energy_MJ_kg", "Weight_lb_gal", "Leaded", "Color"]
    )
    loadCSV(
        f"{CSV_DIR}/EngineType.csv", 
        "EngineType", 
        ["ModelName", "Thrust", "CylinderCount", "CylinderConfig", "PropSize"]
    )
    loadCSV(
        f"{CSV_DIR}/SeatingArrangement.csv", 
        "SeatingArrangement", 
        ["ID", "FirstClassCount", "BusinessClassCount", "EconomyCount", "PilotCount", "OtherCount"]
    )

    # Models
    loadCSV(
        f"{CSV_DIR}/Model.csv", 
        "Model", 
        ["VariantName", "AircraftName", "Range", "VariantOf"]
    )

    # Model Relationships
    loadCSV(
        f"{CSV_DIR}/Model_Engine_Usage.csv", 
        "Model_Engine_Usage", 
        ["ModelVariantName", "EngineModelName", "NumberOfEngines"]
    )
    loadCSV(
        f"{CSV_DIR}/Model_Manufacturer.csv", 
        "Model_Manufacturer", 
        ["ModelVariantName", "ManufacturerName", "Country", "YearEnd"]
    )
    loadCSV(
        f"{CSV_DIR}/Model_Seating.csv", 
        "Model_Seating", 
        ["ModelVariantName", "SeatingID"]
    )
    
    # Records
    loadCSV(
        f"{CSV_DIR}/SpeedRecord.csv", 
        "SpeedRecord", 
        ["RecordID", "ReportedModel", "ModelVariantName", "DateSet", "SpeedKph", "Sponsor", "Description"]
    )
    
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    main()