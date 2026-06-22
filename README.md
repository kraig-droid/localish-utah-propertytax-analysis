# Utah Property Tax Analysis

A Python-based project for analyzing and visualizing Utah property tax rates across cities and tax areas, with a focus on comparing local tax burdens.

## Overview

This project processes official Utah State Tax Commission property tax data to:
- Store tax rate information in a SQLite database
- Calculate "local-ish" tax rates (excluding county, school, and library rates)
- Compare tax burdens across Utah cities
- Generate interactive HTML visualizations
- Analyze specific areas of interest (e.g., Ogden Valley City)

## Data Sources

- Contact the https://tax.utah.gov/property-tax-contact/ to get an xlsx file of tax rates by tax area. I called someone in the TAX RATES & STATISTICS section.
  - the data is available online in a PDF, but it does not process easily with pdfplumber and the like, nor with converting to images and OCR and then pdfplumber. I failed with both of those approaches.
- Go to https://gis.utah.gov/products/sgid/boundaries/municipal/, click Utah Municipal Boundaries in the SGID on ArcGIS, click Download, and get a csv.

## Usage

1. Run `uv run jupyter nbconvert --to notebook --execute property_tax_comparisons.ipynb` to process the source data and create the SQLite database
2. Run `uv run python export_city_data.py` to export city tax burden data
3. Run `uv run python export_entity_data.py` to export entity breakdown data
4. Run `uv run python generate_html.py` to generate the HTML visualization
