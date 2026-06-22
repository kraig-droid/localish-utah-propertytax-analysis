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

```bash
uv run jupyter nbconvert --to notebook --execute property_tax_comparisons.ipynb  # process the source data and create the SQLite database
uv run python export_city_data.py  # export city tax burden data
uv run python export_entity_data.py  # export entity breakdown data
uv run python generate_html.py  # generate the HTML visualization
```

## LLM Disclosure
This project was
- mostly built using Devin/Windsurf with me propmting frequently (models: SWE-1.6, Claude 4.5 Sonnet)
- reviewed using Claude Code Opus 4.8 (high) and patched with Sonnet 4.6 (medium)
