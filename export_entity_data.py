import sqlite3
import pandas as pd
import json
from pathlib import Path

# Connect to database
db_path = Path("data/property_tax.db")
conn = sqlite3.connect(db_path)

# Load the city data to get max tax areas
city_data_path = Path("data/city_tax_burden.json")
with open(city_data_path, 'r') as f:
    cities_data = json.load(f)

# Build entity breakdown for each city's max tax area
entities_data = {}

for city in cities_data:
    city_name = city['city_name']
    county = city['county']
    max_tax_area = city['max_tax_area']
    max_tax_area_ext = city['max_tax_area_ext']
    
    # Query for entities in this tax area (excluding county 1xxx, school 2xxx, and PID 5xxx)
    query = f"""
    SELECT EntityCode, EntityName, FinalRate
    FROM tax_rates
    WHERE County = '{county}'
      AND TaxArea = '{max_tax_area}'
      AND TaxAreaExtension = {max_tax_area_ext}
      AND CAST(EntityCode AS INTEGER) / 1000 NOT IN (1, 2, 5)
      AND EntityCode != 3071
      AND EntityName NOT LIKE '%LIBRAR%'
    ORDER BY FinalRate DESC
    """
    
    entities_df = pd.read_sql_query(query, conn)
    
    # Convert to list of dicts
    entities_list = []
    for _, row in entities_df.iterrows():
        entities_list.append({
            'entity_code': int(row['EntityCode']),
            'entity_name': row['EntityName'],
            'rate': float(row['FinalRate'])
        })
    
    entities_data[city_name] = entities_list

# Rename original Ogden Valley City to (2025 RATE) and add proposed variant
if 'OGDEN VALLEY CITY' in entities_data:
    ogden_valley_entities = entities_data['OGDEN VALLEY CITY']
    # Rename original to (2025 RATE)
    entities_data['OGDEN VALLEY CITY (2025 RATE)'] = ogden_valley_entities
    del entities_data['OGDEN VALLEY CITY']

    # Add proposed variant with 0.000985 rate
    # Replace 6090 (MUNICIPAL TYPE SERVICES, 0.000159) with 3199 (OGDEN VALLEY CITY, 0.000985)
    proposed_entities = [
        {
            'entity_code': 3199,
            'entity_name': 'OGDEN VALLEY CITY',
            'rate': 0.000985
        }
    ]
    # Add all other entities except 6090
    for entity in ogden_valley_entities:
        if entity['entity_code'] != 6090:
            proposed_entities.append(entity)
    # Sort by rate descending
    proposed_entities.sort(key=lambda x: x['rate'], reverse=True)
    entities_data['OGDEN VALLEY CITY (PROPOSED RATE)'] = proposed_entities
elif 'OGDEN VALLEY CITY (2025 RATE)' in entities_data:
    # Handle case where city_tax_burden.json was already regenerated
    ogden_valley_entities = entities_data['OGDEN VALLEY CITY (2025 RATE)']

    # Add proposed variant with 0.000985 rate
    # Replace 6090 (MUNICIPAL TYPE SERVICES, 0.000159) with 3199 (OGDEN VALLEY CITY, 0.000985)
    proposed_entities = [
        {
            'entity_code': 3199,
            'entity_name': 'OGDEN VALLEY CITY',
            'rate': 0.000985
        }
    ]
    # Add all other entities except 6090
    for entity in ogden_valley_entities:
        if entity['entity_code'] != 6090:
            proposed_entities.append(entity)
    # Sort by rate descending
    proposed_entities.sort(key=lambda x: x['rate'], reverse=True)
    entities_data['OGDEN VALLEY CITY (PROPOSED RATE)'] = proposed_entities

# Save to JSON
output_path = Path("data/entity_breakdown.json")
with open(output_path, 'w') as f:
    json.dump(entities_data, f, indent=2)

print(f"Exported entity breakdown for {len(entities_data)} cities to {output_path}")

conn.close()
