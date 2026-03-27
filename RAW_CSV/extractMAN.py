#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python3Packages.pandas

import csv

def process_csv(input_file, output_file):
    # Dictionary to handle potential duplicates while reading
    # Using the Base Model name as the key
    data_map = {}

    try:
        with open(input_file, mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Clean the data: remove leading/trailing whitespace
                model = row["Base Model"].strip()
                variants = row["Variants"].strip()

                # Adding to dictionary automatically handles duplicate "Base Model" names
                # by keeping the latest entry found.
                data_map[model] = variants

        # Convert dictionary back to a list of tuples and sort by the model name
        sorted_data = sorted(data_map.items())

        # Write the cleaned and sorted data to a new CSV
        with open(output_file, mode="w", encoding="utf-8", newline="") as csvfile:
            fieldnames = ["Base Model", "Variants"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for model, variants in sorted_data:
                writer.writerow({"Base Model": model, "Variants": variants})

        print(f"Successfully processed {len(sorted_data)} unique rows.")
        print(f"Sorted data saved to: {output_file}")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except KeyError:
        print("Error: The CSV header must contain 'Base Model' and 'Variants'.")

if __name__ == "__main__":
    process_csv("variants.csv", "sorted_variants.csv")