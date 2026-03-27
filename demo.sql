BEGIN;

-- insert new manufacturer
INSERT INTO "Manufacturer" ("Name", "YearFounded")
VALUES ('Noche Airworks', 2026);

-- insert new fuel type
INSERT INTO "FuelType" ("Name", "Octane", "Energy_MJ_kg", "Weight_lb_gal", "Leaded", "Color")
VALUES ('Noche Fuel', 100, 43.5, 6.1, FALSE, 'Blue');

-- update manufacturer
UPDATE "Manufacturer"
SET "YearFounded" = 2025
WHERE "Name" = 'Noche Airworks';

-- update seating arrangement (+5)
UPDATE "SeatingArrangement"
SET "EconomyCount" = "EconomyCount" + 5
WHERE "ID" = (
  SELECT MIN("ID") FROM "SeatingArrangement"
);

-- delete from manufacturer
DELETE FROM "Manufacturer"
WHERE "Name" = 'Noche Airworks';

-- delete from speed record
DELETE FROM "SpeedRecord"
WHERE "DateSet" = (
  SELECT MIN("DateSet") FROM "SpeedRecord"
);

-- filter/sorting models
SELECT
  m."AircraftName",
  m."VariantName",
  m."Range"
FROM "Model" m
WHERE m."AircraftName" ILIKE '%BOEING%'
ORDER BY m."Range" DESC NULLS LAST, m."VariantName"
LIMIT 20;

-- aggregate avg cylinders and median range
SELECT
  AVG(e."CylinderCount") AS avg_cylinders,
  percentile_cont(0.5) WITHIN GROUP (ORDER BY m."Range") AS median_model_range
FROM "EngineType" e
CROSS JOIN "Model" m
WHERE e."CylinderCount" IS NOT NULL
  AND m."Range" IS NOT NULL;

ROLLBACK;