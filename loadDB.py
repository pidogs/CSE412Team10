import csv
import os
import psycopg2

CSV_DIR = "CSV_FAKE"

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
        "ModelSeating",
        "EngineFuel",
        "EngineManufacturer",
        "ModelManufacturer",
        "ModelEngineUsage",
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
        "Name" VARCHAR(255) PRIMARY KEY,
        "Octane" INT,
        "Energy_MJ_kg" FLOAT,
        "Weight_lb_gal" FLOAT,
        "Leaded" BOOLEAN,
        "Color" VARCHAR(50)
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
        "AircraftName" VARCHAR(255) REFERENCES "Aircraft"("Name"),
        "VariantName" VARCHAR(255),
        "Range" FLOAT,
        PRIMARY KEY("VariantName", "AircraftName")
    );

    CREATE TABLE "ModelEngineUsage" (
        "ModelAircraftName" VARCHAR(255),
        "ModelVariantName" VARCHAR(255),
        "EngineModelName" VARCHAR(255) REFERENCES "EngineType"("ModelName"),
        "NumberOfEngines" INT,
        FOREIGN KEY ("ModelAircraftName", "ModelVariantName") REFERENCES "Model"("AircraftName", "VariantName"),
        PRIMARY KEY ("ModelAircraftName", "ModelVariantName", "EngineModelName")
    );

    CREATE TABLE "ModelManufacturer" (
        "ModelAircraftName" VARCHAR(255),
        "ModelVariantName" VARCHAR(255),
        "ManufacturerName" VARCHAR(255) REFERENCES "Manufacturer"("Name"),
        "Country" VARCHAR(255),
        "YearEnd" INT,
        FOREIGN KEY ("ModelAircraftName", "ModelVariantName") REFERENCES "Model"("AircraftName", "VariantName"),
        PRIMARY KEY ("ModelAircraftName", "ModelVariantName", "ManufacturerName")
    );

    CREATE TABLE "EngineManufacturer" (
        "EngineModelName" VARCHAR(255) PRIMARY KEY REFERENCES "EngineType"("ModelName"),
        "ManufacturerName" VARCHAR(255) REFERENCES "Manufacturer"("Name"),
        "Country" VARCHAR(255),
        "YearEnd" INT
    );

    CREATE TABLE "EngineFuel" (
        "EngineModelName" VARCHAR(255) PRIMARY KEY REFERENCES "EngineType"("ModelName"),
        "FuelName" VARCHAR(255) REFERENCES "FuelType"("Name")
    );
    
    CREATE TABLE "ModelSeating" (
        "ModelAircraftName" VARCHAR(255),
        "ModelVariantName" VARCHAR(255),
        "SeatingID" INT REFERENCES "SeatingArrangement"("ID"),
        FOREIGN KEY ("ModelAircraftName", "ModelVariantName") REFERENCES "Model"("AircraftName", "VariantName"),
        PRIMARY KEY ("ModelAircraftName", "ModelVariantName", "SeatingID")
    );

    CREATE TABLE "SpeedRecord" (
        "RecordID" INT PRIMARY KEY,
        "ModelAircraftName" VARCHAR(255),
        "ModelVariantName" VARCHAR(255),
        "DateSet" DATE,
        "Speed_kph" FLOAT,
        "Sponsor" VARCHAR(255),
        "Description" TEXT,
        FOREIGN KEY ("ModelAircraftName", "ModelVariantName") REFERENCES "Model"("AircraftName", "VariantName")
    );
    """
    cursor.execute(schema)
    cursor.close()
    conn.close()
    print("Tables created successfully")


def loadCSV(file_path, table_name):
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} not found")
        return

    print(f"Loading data into {table_name} from {file_path}")
    conn = getConnection()
    cursor = conn.cursor()

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
                
        # Prepare insert query with quoted column names
        quoted_cols = [f'"{col}"' for col in header]
        cols = ", ".join(quoted_cols)
        placeholders = ", ".join(["%s"] * len(header))
        query = f'INSERT INTO "{table_name}" ({cols}) VALUES ({placeholders})'

        for row in reader:
            # Replace empty strings with None so database will use NULLs
            cleanRow = [val if val.strip() != "" else None for val in row]
            
            # if missing rows then pad rows
            while len(cleanRow) < len(header):
                cleanRow.append(None)
            
            cursor.execute(query, cleanRow[:len(header)])

    conn.commit()
    cursor.close()
    conn.close()


def main():
    print("RESET DB")
    resetDatabase()
    
    # Parents
    loadCSV(f"{CSV_DIR}/Aircraft.csv", "Aircraft")
    loadCSV(f"{CSV_DIR}/Manufacturer.csv", "Manufacturer")
    loadCSV(
        f"{CSV_DIR}/FuelType.csv", 
        "FuelType", 
    )
    loadCSV(
        f"{CSV_DIR}/EngineType.csv", 
        "EngineType", 
    )
    loadCSV(
        f"{CSV_DIR}/SeatingArrangement.csv", 
        "SeatingArrangement", 
    )

    # Models
    loadCSV(
        f"{CSV_DIR}/Model.csv", 
        "Model", 
    )

    # Model Relationships
    loadCSV(
        f"{CSV_DIR}/ModelEngineUsage.csv", 
        "ModelEngineUsage", 
    )
    loadCSV(
        f"{CSV_DIR}/ModelManufacturer.csv", 
        "ModelManufacturer", 
    )
    loadCSV(
        f"{CSV_DIR}/EngineManufacturer.csv", 
        "EngineManufacturer", 
    )
    loadCSV(
        f"{CSV_DIR}/EngineFuel.csv", 
        "EngineFuel", 
    )
    loadCSV(
        f"{CSV_DIR}/ModelSeating.csv", 
        "ModelSeating", 
    )
    
    # Records
    loadCSV(
        f"{CSV_DIR}/SpeedRecord.csv", 
        "SpeedRecord", 
    )
    
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    main()