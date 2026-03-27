import random
import string
FAKE_DIR = "CSV_FAKE"

def gen_int(low=0, high=100):
    return str(random.randint(low, high))

def gen_varchar(min_len = 10, max_len = 20):
    return ''.join(random.choices(string.ascii_letters+" ", k=random.randint(min_len, max_len)))

def gen_float(low=10, high=100):
    return str(random.random()*(high-low)+low)

def gen_boolean():
    return str(random.random() < 0.5)

def gen_date():
    year = str(gen_int(1900,2026)).rjust(4, "0")
    month = str(gen_int(1,12)).rjust(2, "0")
    day = str(gen_int(1,28)).rjust(2, "0")
    return "-".join((year, month, day))

def gen_aircraft(num_rows):
    keys = set()
    while len(keys) < num_rows:
        keys.add((gen_varchar(), ))
    result = []
    for key in keys:
        key_list = list(key)
        result.append(key_list)
    result.append(["Boeing"]) # Add some recognizable data
    return result

def gen_manufacturer(num_rows):
    keys = set()
    while len(keys) < num_rows:
        keys.add((gen_varchar(), ))
    result = []
    for key in keys:
        key_list = list(key)
        key_list.append(gen_int(1800, 2026))
        result.append(key_list)
    return result

def gen_fuel_type(num_rows):
    keys = set()
    while len(keys) < num_rows:
        keys.add((gen_varchar(), ))
    result = []
    for key in keys:
        key_list = list(key)
        key_list.append(gen_int())
        key_list.append(gen_float())
        key_list.append(gen_float())
        key_list.append(gen_boolean())
        key_list.append(gen_varchar())
        result.append(key_list)
    return result

def gen_engine_type(num_rows):
    keys = set()
    while len(keys) < num_rows:
        keys.add((gen_varchar(), ))
    result = []
    for key in keys:
        key_list = list(key)
        key_list.append(gen_float())
        key_list.append(gen_int())
        key_list.append(gen_varchar())
        key_list.append(gen_float())
        result.append(key_list)
    return result

def gen_seating_arrangement(num_rows):
    keys = set()
    while len(keys) < num_rows:
        keys.add((gen_int(1, num_rows*100), ))
    result = []
    for key in keys:
        key_list = list(key)
        key_list.append(gen_int())
        key_list.append(gen_int())
        key_list.append(gen_int())
        key_list.append(gen_int())
        key_list.append(gen_int())
        result.append(key_list)
    return result

def gen_model(num_rows, aircraft_data, aircraft_filter):
    keys = set()
    while len(keys) < num_rows:
        keys.add(
            tuple(aircraft_filter(random.choice(aircraft_data))) +
            (gen_varchar(), )
        )
    result = []
    for key in keys:
        key_list = list(key)
        key_list.append(gen_float())
        result.append(key_list)
    return result

def gen_model_engine(num_rows, model_data, model_filter, engine_data, engine_filter):
    keys = set()
    while len(keys) < num_rows:
        keys.add(
            tuple(model_filter(random.choice(model_data))) +
            tuple(engine_filter(random.choice(engine_data)))
        )
    result = []
    for key in keys:
        key_list = list(key)
        key_list.append(gen_int())
        result.append(key_list)
    return result

def gen_model_manufacturer(num_rows, model_data, model_filter, manufacturer_data, manufacturer_filter):
    keys = set()
    while len(keys) < num_rows:
        keys.add(
            tuple(model_filter(random.choice(model_data))) +
            tuple(manufacturer_filter(random.choice(manufacturer_data)))
        )
    result = []
    for key in keys:
        key_list = list(key)
        key_list.append(gen_varchar())
        key_list.append(gen_int(1800, 2026))
        result.append(key_list)
    return result

def gen_engine_manufacturer(num_rows, engine_data, engine_filter, manufacturer_data, manufacturer_filter):
    keys = set()
    while len(keys) < num_rows:
        keys.add(tuple(engine_filter(random.choice(engine_data))))
    result = []
    for key in keys:
        key_list = list(key)
        for col in manufacturer_filter(random.choice(manufacturer_data)):
            key_list.append(col)
        key_list.append(gen_varchar())
        key_list.append(gen_int(1800, 2026))
        result.append(key_list)
    return result

def gen_engine_fuel(num_rows, engine_data, engine_filter, fuel_data, fuel_filter):
    keys = set()
    while len(keys) < num_rows:
        keys.add(tuple(engine_filter(random.choice(engine_data))))
    result = []
    for key in keys:
        key_list = list(key)
        for col in fuel_filter(random.choice(fuel_data)):
            key_list.append(col)
        result.append(key_list)
    return result

def gen_model_seating(num_rows, model_data, model_filter, seat_arrangement_data, seat_arrangement_filter):
    keys = set()
    while len(keys) < num_rows:
        keys.add(
            tuple(model_filter(random.choice(model_data))) +
            tuple(seat_arrangement_filter(random.choice(seat_arrangement_data)))
        )
    result = []
    for key in keys:
        key_list = list(key)
        result.append(key_list)
    return result

def gen_speed_record(num_rows, model_data, model_filter):
    keys = set()
    while len(keys) < num_rows:
        keys.add((gen_varchar(), gen_varchar()))
    result = []
    for key in keys:
        key_list = list(key)
        for col in model_filter(random.choice(model_data)):
            key_list.append(col)
        key_list.append(gen_date())
        key_list.append(gen_float())
        key_list.append(gen_varchar())
        result.append(key_list)
    return result

if __name__ == "__main__":
    aircraft_data = gen_aircraft(1000)
    manufacturer_data = gen_manufacturer(500)
    fuel_data = gen_fuel_type(100)
    engine_data = gen_engine_type(100)
    seat_arrangement_data = gen_seating_arrangement(200)
    model_data = gen_model(10000, aircraft_data, lambda x: x[0:1])
    model_engine_data = gen_model_engine(5000, model_data, lambda x:x[0:2], engine_data, lambda x:x[0:1])
    model_manufacturer_data = gen_model_manufacturer(100, model_data, lambda x:x[0:2], manufacturer_data, lambda x:x[0:1])
    engine_manufacturer_data = gen_engine_manufacturer(100, engine_data, lambda x:x[0:1], manufacturer_data, lambda x:x[0:1])
    engine_fuel_data = gen_engine_fuel(100, engine_data, lambda x:x[0:1], fuel_data, lambda x:x[0:1])
    model_seating_data = gen_model_seating(100, model_data, lambda x:x[0:2], seat_arrangement_data, lambda x:x[0:1])
    speed_record_data = gen_speed_record(100, model_data, lambda x:x[0:2])

    with open(FAKE_DIR+"/Aircraft.csv", "w") as f:
        cols = ["Name"]
        contents = [cols]+aircraft_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)

    with open(FAKE_DIR+"/Manufacturer.csv", "w") as f:
        cols = ["Name", "YearFounded"]
        contents = [cols]+manufacturer_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)

    with open(FAKE_DIR+"/FuelType.csv", "w") as f:
        cols = ["Name", "Octane", "Energy_MJ_kg", "Weight_lb_gal", "Leaded", "Color"]
        contents = [cols]+fuel_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)

    with open(FAKE_DIR+"/EngineType.csv", "w") as f:
        cols = ["ModelName", "Thrust", "CylinderCount", "CylinderConfig", "PropSize"]
        contents = [cols]+engine_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)
    
    with open(FAKE_DIR+"/SeatingArrangement.csv", "w") as f:
        cols = ["ID", "FirstClassCount", "BusinessClassCount", "EconomyCount", "PilotCount", "OtherCount"]
        contents = [cols]+seat_arrangement_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)

    with open(FAKE_DIR+"/Model.csv", "w") as f:
        cols = ["AircraftName", "VariantName", "Range"]
        contents = [cols]+model_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)

    with open(FAKE_DIR+"/ModelEngineUsage.csv", "w") as f:
        cols = ["ModelAircraftName", "ModelVariantName", "EngineModelName", "NumberOfEngines"]
        contents = [cols]+model_engine_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)

    with open(FAKE_DIR+"/ModelManufacturer.csv", "w") as f:
        cols = ["ModelAircraftName", "ModelVariantName", "ManufacturerName", "Country", "YearEnd"]
        contents = [cols]+model_manufacturer_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)

    with open(FAKE_DIR+"/EngineManufacturer.csv", "w") as f:
        cols = ["EngineModelName", "ManufacturerName", "Country", "YearEnd"]
        contents = [cols]+engine_manufacturer_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)

    with open(FAKE_DIR+"/EngineFuel.csv", "w") as f:
        cols = ["EngineModelName", "FuelName"]
        contents = [cols]+engine_fuel_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)

    with open(FAKE_DIR+"/ModelSeating.csv", "w") as f:
        cols = ["ModelAircraftName", "ModelVariantName", "SeatingID"]
        contents = [cols]+model_seating_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)

    with open(FAKE_DIR+"/SpeedRecord.csv", "w") as f:
        cols = ["Name", "Sponsor", "ModelAircraftName", "ModelVariantName", "DateSet", "Speed_kph", "Description"]
        contents = [cols]+speed_record_data
        contents = [",".join(row)+"\n" for row in contents]
        f.writelines(contents)