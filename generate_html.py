import json
from pathlib import Path

# Read the JSON data
with open("derived_data/city_tax_burden.json", "r") as f:
    cities_data = json.load(f)

with open("derived_data/entity_breakdown.json", "r") as f:
    entities_data = json.load(f)

# HTML template
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Utah Local-Ish Tax Burden Comparison</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.5;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 24px;
        }

        h1 {
            font-size: 28px;
            margin-bottom: 8px;
            color: #333;
        }

        .subtitle {
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }

        .controls {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
        }

        .sort-btn {
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }

        .sort-btn:hover {
            background: #f0f0f0;
        }

        .sort-btn.active {
            background: #0066cc;
            color: white;
            border-color: #0066cc;
        }

        .show-all-btn {
            padding: 8px 16px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }

        .show-all-btn:hover {
            background: #218838;
        }

        .show-all-btn.hidden {
            display: none;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        thead {
            position: sticky;
            top: 0;
            background: white;
            z-index: 10;
        }

        th {
            text-align: left;
            padding: 6px 12px;
            border-bottom: 2px solid #ddd;
            font-weight: 600;
            color: #333;
            cursor: pointer;
            user-select: none;
        }

        th:hover {
            background: #f5f5f5;
        }

        td {
            padding: 4px 12px;
            border-bottom: 1px solid #eee;
        }

        tr:hover {
            background: #f9f9f9;
        }

        .ogden-valley {
            background: #fff3cd !important;
            border-left: 4px solid #ffc107;
        }

        .ogden-valley:hover {
            background: #ffe69c !important;
        }

        .ogden-valley-proposed {
            background: #d1ecf1 !important;
            border-left: 4px solid #17a2b8;
        }

        .ogden-valley-proposed:hover {
            background: #bee5eb !important;
        }

        .expand-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 18px;
            padding: 0 8px;
            color: #666;
            transition: transform 0.2s;
        }

        .expand-btn:hover {
            color: #333;
        }

        .expand-btn.expanded {
            transform: rotate(90deg);
        }

        .entity-row {
            display: none;
            background: #fafafa;
        }

        .entity-row.visible {
            display: table-row;
        }

        .entity-cell {
            padding: 3px 12px 3px 48px;
            border-bottom: 1px solid #eee;
            font-size: 13px;
            color: #555;
        }

        .entity-name {
            font-weight: 500;
        }

        .entity-rate {
            font-family: 'Courier New', monospace;
        }

        .rate-cell {
            font-family: 'Courier New', monospace;
        }

        .numeric {
            text-align: right;
        }

        .sortable {
            cursor: pointer;
            user-select: none;
            position: relative;
        }

        .sortable:hover {
            background-color: #f5f5f5;
        }

        .sortable.sorted {
            background-color: #e8f4fd;
            font-weight: 600;
        }

        .sort-indicator {
            margin-left: 5px;
            opacity: 0.3;
        }

        .sortable.sorted .sort-indicator {
            opacity: 1;
        }

        .hidden-row {
            display: none;
        }

        .info {
            font-size: 12px;
            color: #888;
            margin-top: 16px;
        }

        .view-toggle {
            display: flex;
            gap: 8px;
            margin-left: 20px;
        }

        .view-btn {
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }

        .view-btn:hover {
            background: #f0f0f0;
        }

        .view-btn.active {
            background: #0066cc;
            color: white;
            border-color: #0066cc;
        }

        .chart-container {
            display: none;
            padding: 0;
        }

        .chart-container.visible {
            display: block;
        }

        .stats-container {
            display: flex;
            flex-wrap: wrap;
            margin-bottom: 20px;
            padding: 16px;
            background: #f8f9fa;
            border-radius: 6px;
        }

        .stat-item {
            flex: 0 0 auto;
            min-width: 80px;
            margin-right: 16px;
        }

        .stat-label {
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
        }

        .stat-value {
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }

        table.hidden {
            display: none;
        }

        .hidden {
            display: none;
        }

        .methodology {
            margin-top: 32px;
            padding: 2px 0 2px 20px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #0066cc;
        }

        .methodology h2 {
            font-size: 20px;
            margin-bottom: 16px;
            color: #333;
        }

        .methodology h3 {
            font-size: 16px;
            margin-top: 16px;
            margin-bottom: 8px;
            color: #555;
        }

        .methodology h4 {
            font-size: 14px;
            margin-top: 12px;
            margin-bottom: 6px;
            color: #444;
            font-weight: 600;
        }

        .methodology p {
            font-size: 14px;
            line-height: 1.6;
            color: #666;
            margin-bottom: 12px;
        }

        .methodology ul {
            font-size: 14px;
            line-height: 1.6;
            color: #666;
            margin-left: 20px;
            margin-bottom: 12px;
        }

        .methodology li {
            margin-bottom: 6px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Utah Local-Ish Tax Burden Comparison</h1>
        <div class="subtitle">Local-ish tax rate (total rate minus county, school, and library rates)</div>
        
        <div class="controls">
            <div class="view-toggle">
                <button class="view-btn" id="tableViewBtn" onclick="switchView('table')">Table</button>
                <button class="view-btn active" id="chartViewBtn" onclick="switchView('chart')">Chart</button>
            </div>
            <label style="margin-left: auto; display: flex; align-items: center; gap: 8px;">
                <input type="checkbox" id="hideSmallCities" checked onchange="toggleSmallCities()">
                <span>hide cities under 5 sq mi</span>
            </label>
        </div>

        <table id="dataTable" class="hidden">
            <thead>
                <tr>
                    <th></th>
                    <th>#</th>
                    <th class="sortable" data-sort="city_name" onclick="sortBy('city_name')">City <span class="sort-indicator"></span></th>
                    <th>County</th>
                    <th class="numeric sortable" data-sort="max_local_rate" onclick="sortBy('max_local_rate')">Max Local-ish Rate <span class="sort-indicator"></span></th>
                    <th class="numeric sortable" data-sort="population" onclick="sortBy('population')">Population <span class="sort-indicator"></span></th>
                    <th class="numeric sortable" data-sort="area_sq_miles" onclick="sortBy('area_sq_miles')">Area (sq mi) <span class="sort-indicator"></span></th>
                </tr>
            </thead>
            <tbody id="tableBody">
            </tbody>
        </table>

        <div id="tableFooter" class="controls" style="margin-top: 20px;">
            <button class="show-all-btn" id="showAllBtn" onclick="showAllCities()">Show All</button>
            <span id="cityCount" style="margin-left: 20px; color: #666;"></span>
        </div>

        <div class="chart-container visible" id="chartContainer">
            <canvas id="rateChart" style="max-height: 400px;"></canvas>
            <div class="stats-container" id="statsContainer">
            </div>
        </div>

        <div class="methodology" id="methodology">
            <h2>Methodology</h2>
            <h3>Tax Areas</h3>
            <p>
                Tax areas are geographic boundaries used by Utah's State Tax Commission to determine which taxing entities apply to a property. Each tax area has a unique code and extension number that identifies the combination of all taxing entities that levy taxes on properties within that area. These entities can include cities, counties, school districts, special service districts, water districts, sewer districts, and other local government entities.
            </p>
            <p>
                <a href="https://files.tax.utah.gov/propertytax/tax-rates/area-rates/taxarearates2025.pdf" target="_blank">Source document: Utah Tax Area Rates 2025 (PDF)</a>
            </p>
            <h3>Local-ish Rate Calculation</h3>
            <h4>Included in local-ish rates</h4>
            <ul>
                <li>City general fund taxes (including county-collected city-level general fund taxes for unincorporated areas)</li>
                <li>Parks and recreation districts</li>
                <li>Water and sewer districts</li>
                <li>Fire protection districts</li>
                <li>Special service districts</li>
                <li>Other local government entities serving specific geographic areas</li>
            </ul>
            <h4>Excluded from local-ish rates</h4>
            <ul>
                <li>County rates - General county government taxes that apply county-wide</li>
                <li>School district rates - Public school funding that applies across entire school districts</li>
                <li>Library rates - County library system taxes</li>
                <li>Public Improvement Districts (PID) - Special districts for infrastructure improvements</li>
            </ul>
            <p>
                <strong>Example: Riverdale (Weber County)</strong><br>
                Tax area: <strong>583 - 0000</strong><br>
            </p>
            <h4>Included rates</h4>
            <ul>
                <li>Riverdale: <em>0.001414</em> (3080)</li>
                <li>Central Weber Sewer Improvement District: <em>0.000540</em> (4010)</li>
                <li>Weber Basin Water Conservancy District: <em>0.000191</em> (4005)</li>
                <li>Weber Area Dispatch 911 and Emergency Services District: <em>0.000163</em> (4320)</li>
                <li>Weber County Mosquito Abatement District: <em>0.000064</em> (4080)</li>
                <li>Roy Water Conservancy Subdistrict: <em>0.000044</em> (4130)</li>
            </ul>
            <h4>Excluded rates</h4>
            <ul>
                <li>Weber: <em>0.001938</em> (1010)</li>
                <li>Multicounty Assessing & Collecting Levy: <em>0.000014</em> (1015)</li>
                <li>County Assessing & Collecting Levy: <em>0.000163</em> (1020)</li>
                <li>Weber County School District: <em>0.005792</em> (2020)</li>
            </ul>
            <h3>Max Local-ish Rate</h3>
            <p>
                For each city, this analysis identifies the tax area with the highest local-ish rate. This represents the maximum local tax burden that residents in that city might face, depending on their specific location within city boundaries. The actual rate for any given property will depend on which tax area it falls within.
            </p>
            <h3>Population and Area Data</h3>
            <ul>
                <li>Data comes from the Utah Geospatial Resource Center (https://gis.utah.gov/products/sgid/boundaries/municipal/).</li>
                <li>Area includes water bodies (may not match land area from other sources).</li>
            </ul>
            <h2>Source Code, Notes, and Original Data</h2>
            <p>
                See <a href="https://github.com/kraig-droid/localish-utah-propertytax-analysis">https://github.com/kraig-droid/localish-utah-propertytax-analysis</a>
            </p>
        </div>

        <div class="info">
            * Ogden Valley City tax areas are those that have OGDEN VALLEY PARKS SERVICE AREA unless they have
            POWDER MOUNTAIN WATER AND SEWER IMPROVEMENT DISTRICT or SUMMIT ROAD OVERLAY DISTRICT.
        </div>
    </div>

    <script>
        // Embedded data
        const citiesData = CITIES_JSON_PLACEHOLDER;
        const entitiesData = ENTITIES_JSON_PLACEHOLDER;

        let currentSort = 'max_local_rate';
        let showAll = false;
        let hideSmallCities = true;
        const INITIAL_DISPLAY = 20;

        function formatRate(rate) {
            return rate.toFixed(6);
        }

        function formatNumber(num) {
            if (num === null || num === 0) return 'N/A';
            return num.toLocaleString();
        }

        function renderTable() {
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';

            // Filter cities based on checkbox
            let filteredCities = citiesData;
            if (hideSmallCities) {
                filteredCities = citiesData.filter(c => c.area_sq_miles >= 5);
            }

            // Find Ogden Valley City indices in filtered data
            const ogdenValleyIndex = filteredCities.findIndex(c => c.city_name === 'OGDEN VALLEY CITY (2025 RATE)');
            const ogdenValleyProposedIndex = filteredCities.findIndex(c => c.city_name === 'OGDEN VALLEY CITY (PROPOSED RATE)');

            // Determine how many to show
            let displayCount = INITIAL_DISPLAY;

            // If either Ogden Valley variant is not shown in the first INITIAL_DISPLAY rows,
            // extend to show both variants plus 2 more rows
            const maxOgdenIndex = Math.max(ogdenValleyIndex, ogdenValleyProposedIndex);
            if (maxOgdenIndex >= INITIAL_DISPLAY) {
                displayCount = Math.max(displayCount, maxOgdenIndex + 3);
            }

            // Ensure at least INITIAL_DISPLAY rows are shown
            displayCount = Math.max(displayCount, INITIAL_DISPLAY);

            if (showAll) {
                displayCount = filteredCities.length;
            }

            for (let i = 0; i < displayCount; i++) {
                const city = filteredCities[i];
                const isOgdenValley = city.city_name === 'OGDEN VALLEY CITY (2025 RATE)';
                const isOgdenValleyProposed = city.city_name === 'OGDEN VALLEY CITY (PROPOSED RATE)';

                const row = document.createElement('tr');
                if (isOgdenValley) {
                    row.className = 'ogden-valley';
                } else if (isOgdenValleyProposed) {
                    row.className = 'ogden-valley-proposed';
                }

                const entities = entitiesData[city.city_name] || [];
                const hasEntities = entities.length > 0;

                row.innerHTML = `
                    <td>
                        ${hasEntities ? `<button class="expand-btn" onclick="toggleExpand('${city.city_name}', this)">▶</button>` : ''}
                    </td>
                    <td>${i + 1}</td>
                    <td>${city.city_name}</td>
                    <td>${city.county}</td>
                    <td class="numeric rate-cell">${formatRate(city.max_local_rate)}</td>
                    <td class="numeric">${formatNumber(city.population)}</td>
                    <td class="numeric">${city.area_sq_miles.toFixed(2)}</td>
                `;
                tbody.appendChild(row);

                // Add entity rows
                if (hasEntities) {
                    // Add tax area row first
                    const taxAreaRow = document.createElement('tr');
                    taxAreaRow.className = 'entity-row';
                    taxAreaRow.dataset.city = city.city_name;
                    const taxAreaStr = `${city.max_tax_area} - ${String(city.max_tax_area_ext).padStart(4, '0')}`;
                    taxAreaRow.innerHTML = `
                        <td></td>
                        <td colspan="6" class="entity-cell">tax area: ${taxAreaStr}</td>
                    `;
                    tbody.appendChild(taxAreaRow);

                    // Add entity rows
                    entities.forEach(entity => {
                        const entityRow = document.createElement('tr');
                        entityRow.className = 'entity-row';
                        entityRow.dataset.city = city.city_name;
                        entityRow.innerHTML = `
                            <td></td>
                            <td></td>
                            <td class="entity-cell">${entity.entity_code}</td>
                            <td class="entity-cell entity-name">${entity.entity_name}</td>
                            <td colspan="4" class="entity-cell entity-rate">${formatRate(entity.rate)}</td>
                        `;
                        tbody.appendChild(entityRow);
                    });
                }
            }

            // Show/hide "Show All" button
            const showAllBtn = document.getElementById('showAllBtn');
            if (showAll || displayCount >= filteredCities.length) {
                showAllBtn.classList.add('hidden');
            } else {
                showAllBtn.classList.remove('hidden');
            }

            // Update city count display
            const cityCountEl = document.getElementById('cityCount');
            cityCountEl.textContent = `${filteredCities.length} available cities`;
        }

        function toggleSmallCities() {
            hideSmallCities = document.getElementById('hideSmallCities').checked;
            showAll = false;
            renderTable();
            // Re-render chart if it's visible
            if (document.getElementById('chartContainer').classList.contains('visible')) {
                renderChart();
            }
        }

        function toggleExpand(cityName, btn) {
            const entityRows = document.querySelectorAll(`.entity-row[data-city="${cityName}"]`);
            entityRows.forEach(row => {
                row.classList.toggle('visible');
            });
            btn.classList.toggle('expanded');
        }

        function sortBy(field) {
            currentSort = field;

            // Update column header styling
            document.querySelectorAll('.sortable').forEach(th => {
                th.classList.remove('sorted');
                const indicator = th.querySelector('.sort-indicator');
                if (indicator) {
                    indicator.textContent = '';
                }
            });

            // Highlight the clicked column and add arrow
            const clickedHeader = document.querySelector(`[data-sort="${field}"]`);
            if (clickedHeader) {
                clickedHeader.classList.add('sorted');
                const indicator = clickedHeader.querySelector('.sort-indicator');
                if (indicator) {
                    indicator.textContent = '▼';
                }
            }

            // Sort all cities including Ogden Valley variants
            citiesData.sort((a, b) => {
                if (field === 'city_name') {
                    return a.city_name.localeCompare(b.city_name);
                } else if (field === 'max_local_rate') {
                    return b.max_local_rate - a.max_local_rate;
                } else if (field === 'population') {
                    return (b.population || 0) - (a.population || 0);
                } else if (field === 'area_sq_miles') {
                    return b.area_sq_miles - a.area_sq_miles;
                }
                return 0;
            });

            showAll = false;
            renderTable();
        }

        function showAllCities() {
            showAll = true;
            renderTable();
        }

        function switchView(view) {
            const tableViewBtn = document.getElementById('tableViewBtn');
            const chartViewBtn = document.getElementById('chartViewBtn');
            const dataTable = document.getElementById('dataTable');
            const chartContainer = document.getElementById('chartContainer');
            const tableFooter = document.getElementById('tableFooter');
            const methodology = document.getElementById('methodology');

            if (view === 'table') {
                tableViewBtn.classList.add('active');
                chartViewBtn.classList.remove('active');
                dataTable.classList.remove('hidden');
                tableFooter.classList.remove('hidden');
                chartContainer.classList.remove('visible');
                methodology.classList.add('hidden');
            } else {
                chartViewBtn.classList.add('active');
                tableViewBtn.classList.remove('active');
                dataTable.classList.add('hidden');
                tableFooter.classList.add('hidden');
                chartContainer.classList.add('visible');
                methodology.classList.remove('hidden');
                renderChart();
            }
        }

        function calculateStats(rates) {
            const sorted = [...rates].sort((a, b) => a - b);
            const n = sorted.length;
            const sum = sorted.reduce((a, b) => a + b, 0);
            const mean = sum / n;
            const median = n % 2 === 0 ? (sorted[n/2 - 1] + sorted[n/2]) / 2 : sorted[Math.floor(n/2)];
            const variance = sorted.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / n;
            const std = Math.sqrt(variance);
            // Use proper percentile calculation: for quartiles, use (n-1) * p
            const q25Index = Math.floor((n - 1) * 0.25);
            const q75Index = Math.floor((n - 1) * 0.75);
            const q25 = sorted[q25Index];
            const q75 = sorted[q75Index];

            return {
                count: n,
                min: sorted[0],
                max: sorted[n - 1],
                mean: mean,
                median: median,
                std: std,
                q25: q25,
                q75: q75
            };
        }

        function renderChart() {
            // Filter cities based on checkbox
            let filteredCities = citiesData;
            if (hideSmallCities) {
                filteredCities = citiesData.filter(c => c.area_sq_miles >= 5);
            }

            const rates = filteredCities.map(c => c.max_local_rate);
            const stats = calculateStats(rates);

            // Create histogram bins
            const binCount = 20;
            const minRate = stats.min;
            const maxRate = stats.max;
            const binWidth = (maxRate - minRate) / binCount;
            const bins = new Array(binCount).fill(0);
            const binLabels = [];

            for (let i = 0; i < binCount; i++) {
                const binStart = minRate + i * binWidth;
                const binEnd = binStart + binWidth;
                binLabels.push(binStart.toFixed(6));
            }

            rates.forEach(rate => {
                const binIndex = Math.min(Math.floor((rate - minRate) / binWidth), binCount - 1);
                bins[binIndex]++;
            });

            // Find Ogden Valley City rates
            const ovc2025 = filteredCities.find(c => c.city_name === 'OGDEN VALLEY CITY (2025 RATE)');
            const ovcProposed = filteredCities.find(c => c.city_name === 'OGDEN VALLEY CITY (PROPOSED RATE)');

            // OVC labels are now drawn directly on the chart, no legend needed
            const ovcLegendHTML = '';

            // Count cities in each quartile for verification
            const q1Count = rates.filter(r => r <= stats.q25).length;
            const q2Count = rates.filter(r => r > stats.q25 && r <= stats.median).length;
            const q3Count = rates.filter(r => r > stats.median && r <= stats.q75).length;
            const q4Count = rates.filter(r => r > stats.q75).length;

            // Add statistics legend
            const statsLegendHTML = `
                <div style="width: 100%; margin-top: 12px; padding-top: 12px; border-top: 1px solid #ddd;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 8px;">Quartiles (by city count):</div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;"><span style="width: 20px; height: 12px; background: rgba(231, 76, 60, 0.3); border: 1px solid #e74c3c;"></span><span style="font-size: 13px;">Q1: ${stats.min.toFixed(6)} - ${stats.q25.toFixed(6)} (${q1Count} cities)</span></div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;"><span style="width: 20px; height: 12px; background: rgba(243, 156, 18, 0.3); border: 1px solid #f39c12;"></span><span style="font-size: 13px;">Q2: ${stats.q25.toFixed(6)} - ${stats.median.toFixed(6)} (${q2Count} cities)</span></div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;"><span style="width: 20px; height: 12px; background: rgba(46, 204, 113, 0.3); border: 1px solid #2ecc71;"></span><span style="font-size: 13px;">Q3: ${stats.median.toFixed(6)} - ${stats.q75.toFixed(6)} (${q3Count} cities)</span></div>
                    <div style="display: flex; align-items: center; gap: 8px;"><span style="width: 20px; height: 12px; background: rgba(52, 152, 219, 0.3); border: 1px solid #3498db;"></span><span style="font-size: 13px;">Q4: ${stats.q75.toFixed(6)} - ${stats.max.toFixed(6)} (${q4Count} cities)</span></div>
                </div>
            `;

            // Render stats
            const statsContainer = document.getElementById('statsContainer');
            statsContainer.innerHTML = `
                <div class="stat-item">
                    <div class="stat-label">Count</div>
                    <div class="stat-value">${stats.count}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Min</div>
                    <div class="stat-value">${stats.min.toFixed(6)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Max</div>
                    <div class="stat-value">${stats.max.toFixed(6)}</div>
                </div>
                <div style="width: 100%;"></div>
                <div class="stat-item">
                    <div class="stat-label">Median</div>
                    <div class="stat-value">${stats.median.toFixed(6)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Std Dev</div>
                    <div class="stat-value">${stats.std.toFixed(6)}</div>
                </div>
                <div style="width: 100%;"></div>
                ${ovc2025 ? `<div class="stat-item"><div class="stat-label">OVC 2025</div><div class="stat-value">${ovc2025.max_local_rate.toFixed(6)}</div></div>` : ''}
                ${ovcProposed ? `<div class="stat-item"><div class="stat-label">OVC Proposed</div><div class="stat-value">${ovcProposed.max_local_rate.toFixed(6)}</div></div>` : ''}
                ${statsLegendHTML}
            `;

            // Destroy existing chart if it exists
            if (window.rateChartInstance) {
                window.rateChartInstance.destroy();
            }

            // Create chart
            const ctx = document.getElementById('rateChart').getContext('2d');

            // Inline plugin that draws quartile regions and OVC marker lines.
            // The x-axis is a category axis, so we convert each rate to a pixel
            // position using the spacing between category ticks.
            const ovcMarkerPlugin = {
                id: 'ovcMarkers',
                beforeDatasetsDraw(chart) {
                    const xAxis = chart.scales.x;
                    const yAxis = chart.scales.y;
                    // Pixel centers of bin 0 and bin 1 give us pixels-per-bin.
                    // Use getPixelForValue (indexes by category value) rather than
                    // getPixelForTick, which breaks when Chart.js auto-skips ticks
                    // on narrow (mobile) canvases.
                    const x0 = xAxis.getPixelForValue(0);
                    const x1 = xAxis.getPixelForValue(1);
                    const pxPerBin = x1 - x0;

                    function pixelForRate(rate) {
                        // Bin i is centered on rate (minRate + (i+0.5)*binWidth),
                        // so the fractional bin index for a rate is:
                        const fracIndex = (rate - minRate) / binWidth - 0.5;
                        return x0 + fracIndex * pxPerBin;
                    }

                    function drawFilledRegion(startRate, endRate, color) {
                        const xStart = pixelForRate(startRate);
                        const xEnd = pixelForRate(endRate);
                        chart.ctx.save();
                        chart.ctx.fillStyle = color;
                        chart.ctx.fillRect(xStart, yAxis.top, xEnd - xStart, yAxis.bottom - yAxis.top);
                        chart.ctx.restore();
                    }

                    // Draw quartile regions behind the main curve
                    drawFilledRegion(stats.min, stats.q25, 'rgba(231, 76, 60, 0.3)');      // Q1 - red
                    drawFilledRegion(stats.q25, stats.median, 'rgba(243, 156, 18, 0.3)');  // Q2 - orange
                    drawFilledRegion(stats.median, stats.q75, 'rgba(46, 204, 113, 0.3)');  // Q3 - green
                    drawFilledRegion(stats.q75, stats.max, 'rgba(52, 152, 219, 0.3)');    // Q4 - blue
                },
                afterDatasetsDraw(chart) {
                    const xAxis = chart.scales.x;
                    const yAxis = chart.scales.y;
                    // Pixel centers of bin 0 and bin 1 give us pixels-per-bin.
                    // Use getPixelForValue (indexes by category value) rather than
                    // getPixelForTick, which breaks when Chart.js auto-skips ticks
                    // on narrow (mobile) canvases.
                    const x0 = xAxis.getPixelForValue(0);
                    const x1 = xAxis.getPixelForValue(1);
                    const pxPerBin = x1 - x0;

                    function pixelForRate(rate) {
                        // Bin i is centered on rate (minRate + (i+0.5)*binWidth),
                        // so the fractional bin index for a rate is:
                        const fracIndex = (rate - minRate) / binWidth - 0.5;
                        return x0 + fracIndex * pxPerBin;
                    }

                    function drawLine(rate, color, dashed = false) {
                        const x = pixelForRate(rate);
                        chart.ctx.save();
                        chart.ctx.strokeStyle = color;
                        chart.ctx.lineWidth = 2;
                        if (dashed) {
                            chart.ctx.setLineDash([6, 4]);
                        }
                        chart.ctx.beginPath();
                        chart.ctx.moveTo(x, yAxis.top);
                        chart.ctx.lineTo(x, yAxis.bottom);
                        chart.ctx.stroke();
                        chart.ctx.restore();
                    }

                    function drawLabel(rate, text, color) {
                        const x = pixelForRate(rate);
                        chart.ctx.save();
                        chart.ctx.font = '12px sans-serif';
                        chart.ctx.fillStyle = color;
                        chart.ctx.textAlign = 'center';
                        chart.ctx.textBaseline = 'top';
                        // Draw label at top of chart
                        chart.ctx.fillText(text, x, yAxis.top + 5);
                        chart.ctx.restore();
                    }

                    // Draw OVC lines on top
                    if (ovc2025) {
                        drawLine(ovc2025.max_local_rate, '#9b59b6', true);
                        drawLabel(ovc2025.max_local_rate, 'OVC 2025', '#9b59b6');
                    }
                    if (ovcProposed) {
                        drawLine(ovcProposed.max_local_rate, '#28a745', true);
                        drawLabel(ovcProposed.max_local_rate, 'OVC Proposed', '#28a745');
                    }
                }
            };

            window.rateChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: binLabels,
                    datasets: [{
                        label: 'Number of Cities',
                        data: bins,
                        backgroundColor: 'rgba(0, 102, 204, 0.5)',
                        borderColor: 'rgba(0, 102, 204, 1)',
                        borderWidth: 1,
                        barPercentage: 1.0,
                        categoryPercentage: 1.0
                    }]
                },
                plugins: [ovcMarkerPlugin],
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: ['How Utah Cities Stack Up on Local-Ish Taxes', '(Number of Cities in Each Tax Rate Range)'],
                            font: { size: 16 },
                            padding: { bottom: 20 }
                        },
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                title: function(context) {
                                    const idx = context[0].dataIndex;
                                    const binStart = minRate + idx * binWidth;
                                    const binEnd = binStart + binWidth;
                                    return `Range: ${binStart.toFixed(6)} - ${binEnd.toFixed(6)}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Tax Rate'
                            },
                            ticks: {
                                maxRotation: 45,
                                minRotation: 45
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Number of Cities'
                            },
                            beginAtZero: true
                        }
                    }
                }
            });

        }

        // Initial render
        // Set initial sort indicator
        const initialHeader = document.querySelector(`[data-sort="${currentSort}"]`);
        if (initialHeader) {
            initialHeader.classList.add('sorted');
            const indicator = initialHeader.querySelector('.sort-indicator');
            if (indicator) {
                indicator.textContent = '▼';
            }
        }
        // Hide table footer initially since chart is the default view
        document.getElementById('tableFooter').classList.add('hidden');
        renderTable();
        // Chart is the default view, so render it on load.
        renderChart();
    </script>
</body>
</html>
"""

# Replace placeholders with actual JSON data
html_content = html_template.replace(
    'CITIES_JSON_PLACEHOLDER',
    json.dumps(cities_data)
).replace(
    'ENTITIES_JSON_PLACEHOLDER',
    json.dumps(entities_data)
)

# Write to file
output_path = Path("docs/index.html")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    f.write(html_content)

print(f"Generated {output_path}")
