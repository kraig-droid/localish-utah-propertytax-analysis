import sqlite3
import pandas as pd
import json
from pathlib import Path

# Connect to database
db_path = Path("derived_data/property_tax.db")
conn = sqlite3.connect(db_path)

# Load population data
pop_file = Path("data/UtahMunicipalBoundaries_221481185616367289.csv")
pop_df = pd.read_csv(pop_file)

def normalize_city_name(name):
    name = str(name).upper().strip()
    for prefix in ('CITY OF ', 'TOWN OF '):
        if name.startswith(prefix):
            name = name[len(prefix):]
    for suffix in (' CITY', ' TOWN'):
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    name = name.replace('.', '')
    return name.strip()

# Manual corrections for DB names that don't match the population CSV
DB_NAME_CORRECTIONS = {
    'SIGUARD': 'SIGURD',
    'EAST CARBON - SUNNYSIDE': 'EAST CARBON',
}

pop_df['name_normalized'] = pop_df['NAME'].apply(normalize_city_name)
pop_df['area_sq_miles'] = pop_df['Shape__Area'] * 3.861e-7

# Query for city tax burden data
query = """
WITH city_tax_areas AS (
    SELECT DISTINCT County, EntityName AS city_name, TaxArea, TaxAreaExtension
    FROM tax_rates
    WHERE CAST(EntityCode AS INTEGER) / 1000 = 3
      AND EntityCode != 3071

    UNION

    SELECT DISTINCT County, 'OGDEN VALLEY CITY' AS city_name, TaxArea, TaxAreaExtension
    FROM tax_rates
    WHERE County = 'WEBER'
      AND EntityName = 'OGDEN VALLEY PARKS SERVICE AREA'
      AND TaxArea NOT IN ('090', '227', '374', '490', '491', '542', '543', '544', '545', '546', '547', '548')
),
breakdown AS (
    SELECT cta.County, cta.city_name, t.TaxArea, t.TaxAreaExtension,
        SUM(t.FinalRate) AS grand_total,
        SUM(CASE WHEN CAST(t.EntityCode AS INTEGER) / 1000 IN (1,2) OR t.EntityName LIKE '%LIBRAR%' THEN t.FinalRate ELSE 0 END) AS county_school,
        SUM(CASE WHEN CAST(t.EntityCode AS INTEGER) / 1000 IN (5) THEN t.FinalRate ELSE 0 END) AS pid_burden,
        SUM(CASE WHEN CAST(t.EntityCode AS INTEGER) / 1000 NOT IN (1,2,5) AND t.EntityName NOT LIKE '%LIBRAR%' THEN t.FinalRate ELSE 0 END) AS city_burden
    FROM tax_rates t
    JOIN city_tax_areas cta ON t.County = cta.County AND t.TaxArea = cta.TaxArea AND t.TaxAreaExtension = cta.TaxAreaExtension
    GROUP BY cta.County, cta.city_name, t.TaxArea, t.TaxAreaExtension
),
ranked_areas AS (
    SELECT 
        County, city_name, TaxArea, TaxAreaExtension, city_burden,
        ROW_NUMBER() OVER (PARTITION BY County, city_name ORDER BY city_burden ASC, TaxAreaExtension ASC) as min_rank,
        ROW_NUMBER() OVER (PARTITION BY County, city_name ORDER BY city_burden DESC, TaxAreaExtension DESC) as max_rank
    FROM breakdown
),
min_max_areas AS (
    SELECT 
        County, city_name,
        MIN(city_burden) AS min_city_burden,
        MAX(city_burden) AS max_city_burden,
        MAX(CASE WHEN min_rank = 1 THEN TaxArea END) AS min_tax_area,
        MAX(CASE WHEN min_rank = 1 THEN TaxAreaExtension END) AS min_tax_area_ext,
        MAX(CASE WHEN max_rank = 1 THEN TaxArea END) AS max_tax_area,
        MAX(CASE WHEN max_rank = 1 THEN TaxAreaExtension END) AS max_tax_area_ext
    FROM ranked_areas
    GROUP BY County, city_name
)
SELECT County, city_name, min_city_burden, max_city_burden, min_tax_area, min_tax_area_ext, max_tax_area, max_tax_area_ext
FROM min_max_areas
ORDER BY County, max_city_burden DESC
"""

city_burden_df = pd.read_sql_query(query, conn)

# Normalize city names for matching
city_burden_df['name_normalized'] = city_burden_df['city_name'].apply(
    lambda n: normalize_city_name(DB_NAME_CORRECTIONS.get(n, n))
)

# Add population and area data
city_burden_df = city_burden_df.merge(
    pop_df[['name_normalized', 'POPLASTCENSUS', 'POPLASTESTIMATE', 'area_sq_miles']],
    on='name_normalized',
    how='left'
)

# For multi-county cities, sum their populations and areas
nan_sum = lambda x: x.sum(min_count=1)
pop_by_city = city_burden_df.groupby('city_name').agg({
    'POPLASTCENSUS': nan_sum,
    'POPLASTESTIMATE': nan_sum,
    'area_sq_miles': nan_sum,
    'County': 'first',
    'min_city_burden': 'first',
    'max_city_burden': 'first',
    'min_tax_area': 'first',
    'min_tax_area_ext': 'first',
    'max_tax_area': 'first',
    'max_tax_area_ext': 'first'
}).reset_index()

# Use POPLASTESTIMATE if available, otherwise POPLASTCENSUS
pop_by_city['population'] = pop_by_city['POPLASTESTIMATE'].fillna(pop_by_city['POPLASTCENSUS'])

# Manual override for Ogden Valley City
pop_by_city.loc[pop_by_city['city_name'] == 'OGDEN VALLEY CITY', 'population'] = 8000

# Convert to JSON-friendly format
cities_data = []
for _, row in pop_by_city.iterrows():
    cities_data.append({
        'city_name': row['city_name'],
        'county': row['County'],
        'min_local_rate': float(row['min_city_burden']),
        'max_local_rate': float(row['max_city_burden']),
        'population': int(row['population']) if pd.notna(row['population']) else None,
        'area_sq_miles': round(float(row['area_sq_miles']), 2),
        'max_tax_area': row['max_tax_area'],
        'max_tax_area_ext': int(row['max_tax_area_ext'])
    })

# Rename original Ogden Valley City to (2025 RATE) and add proposed variant
ogden_valley = next((c for c in cities_data if c['city_name'] == 'OGDEN VALLEY CITY'), None)
if ogden_valley:
    # Rename original to (2025 RATE)
    ogden_valley['city_name'] = 'OGDEN VALLEY CITY (2025 RATE)'

    # Add proposed variant with 0.000985 rate
    # Calculate proposed rate: replace 6090 (0.000159) with 3199 (0.000985)
    # Difference: 0.000985 - 0.000159 = 0.000826
    proposed_city = ogden_valley.copy()
    proposed_city['city_name'] = 'OGDEN VALLEY CITY (PROPOSED RATE)'
    proposed_city['max_local_rate'] = ogden_valley['max_local_rate'] - 0.000159 + 0.000985
    proposed_city['min_local_rate'] = ogden_valley['min_local_rate'] - 0.000159 + 0.000985
    proposed_city['proposed'] = True
    cities_data.append(proposed_city)

# Sort by max local rate descending
cities_data.sort(key=lambda x: x['max_local_rate'], reverse=True)

# Save to JSON
output_path = Path("derived_data/city_tax_burden.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(cities_data, f, indent=2)

print(f"Exported {len(cities_data)} cities to {output_path}")

conn.close()
