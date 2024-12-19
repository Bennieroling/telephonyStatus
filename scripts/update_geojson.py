import json

# Load the existing GeoJSON file
file_path = "countries.geo.json"  # Replace with the path to your file if different

# Load the GeoJSON data
with open(file_path, 'r') as file:
    geojson_data = json.load(file)

# Update each feature to ensure the ADMIN property matches the name property
for feature in geojson_data.get('features', []):
    name_value = feature.get('properties', {}).get('name')
    if name_value:
        feature['properties']['ADMIN'] = name_value  # Add ADMIN if missing

# Save the updated GeoJSON file
updated_file_path = "updated_countries.geo.json"
with open(updated_file_path, 'w') as updated_file:
    json.dump(geojson_data, updated_file, indent=2)

print(f"Updated file saved as {updated_file_path}")
