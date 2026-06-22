import json
from pathlib import Path

# Read the JSON data
with open("data/city_tax_burden.json", "r") as f:
    cities_data = json.load(f)

with open("data/entity_breakdown.json", "r") as f:
    entities_data = json.load(f)

# HTML template
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Utah City Tax Burden Comparison</title>
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
            padding: 20px 0;
        }

        .chart-container.visible {
            display: block;
        }

        .stats-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
            padding: 16px;
            background: #f8f9fa;
            border-radius: 6px;
        }

        .stat-item {
            flex: 1;
            min-width: 120px;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Utah City Tax Burden Comparison</h1>
        <div class="subtitle">Local-ish tax rate (total rate minus county and school rates) for cities with area ≥ 5 sq mi</div>
        
        <div class="controls">
            <button class="show-all-btn" id="showAllBtn" onclick="showAllCities()">Show All</button>
            <span id="cityCount" style="margin-left: 20px; color: #666;"></span>
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

        <div class="chart-container visible" id="chartContainer">
            <div class="stats-container" id="statsContainer">
            </div>
            <canvas id="rateChart" style="max-height: 400px;"></canvas>
        </div>

        <div class="info">
            * Ogden Valley City (incorporated 2024) is identified by OGDEN VALLEY PARKS SERVICE AREA. Population manually set to 8,000.
            * Ogden Valley City excludes tax areas with POWDER MOUNTAIN WATER AND SEWER IMPROVEMENT DISTRICT or SUMMIT ROAD OVERLAY DISTRICT.
            * Ogden Valley City (PROPOSED RATE) shows the tax burden if the city adopts the new rate of 0.000985 for city-level taxes.
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
            const showAllBtn = document.getElementById('showAllBtn');

            if (view === 'table') {
                tableViewBtn.classList.add('active');
                chartViewBtn.classList.remove('active');
                dataTable.classList.remove('hidden');
                chartContainer.classList.remove('visible');
                showAllBtn.classList.remove('hidden');
            } else {
                chartViewBtn.classList.add('active');
                tableViewBtn.classList.remove('active');
                dataTable.classList.add('hidden');
                chartContainer.classList.add('visible');
                showAllBtn.classList.add('hidden');
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
            const q25 = sorted[Math.floor(n * 0.25)];
            const q75 = sorted[Math.floor(n * 0.75)];

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

            // Add OVC legend to stats
            let ovcLegendHTML = '';
            if (ovc2025 || ovcProposed) {
                ovcLegendHTML = `
                    <div style="width: 100%; margin-top: 12px; padding-top: 12px; border-top: 1px solid #ddd;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 8px;">Ogden Valley City:</div>
                        ${ovc2025 ? `<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;"><span style="width: 20px; height: 3px; background: repeating-linear-gradient(90deg, #9b59b6 0, #9b59b6 4px, transparent 4px, transparent 8px); border: 1px solid #9b59b6;"></span><span style="font-size: 13px;">2025 Rate: ${ovc2025.max_local_rate.toFixed(6)}</span></div>` : ''}
                        ${ovcProposed ? `<div style="display: flex; align-items: center; gap: 8px;"><span style="width: 20px; height: 3px; background: repeating-linear-gradient(90deg, #28a745 0, #28a745 4px, transparent 4px, transparent 8px); border: 1px solid #28a745;"></span><span style="font-size: 13px;">Proposed Rate: ${ovcProposed.max_local_rate.toFixed(6)}</span></div>` : ''}
                    </div>
                `;
            }

            // Add statistics legend
            const statsLegendHTML = `
                <div style="width: 100%; margin-top: 12px; padding-top: 12px; border-top: 1px solid #ddd;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 8px;">Statistics:</div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;"><span style="width: 20px; height: 2px; background: #e74c3c;"></span><span style="font-size: 13px;">Mean: ${stats.mean.toFixed(6)}</span></div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;"><span style="width: 20px; height: 2px; background: #3498db;"></span><span style="font-size: 13px;">Median: ${stats.median.toFixed(6)}</span></div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;"><span style="width: 20px; height: 2px; background: repeating-linear-gradient(90deg, #f39c12 0, #f39c12 4px, transparent 4px, transparent 8px); border: 1px solid #f39c12;"></span><span style="font-size: 13px;">25th Percentile: ${stats.q25.toFixed(6)}</span></div>
                    <div style="display: flex; align-items: center; gap: 8px;"><span style="width: 20px; height: 2px; background: repeating-linear-gradient(90deg, #f39c12 0, #f39c12 4px, transparent 4px, transparent 8px); border: 1px solid #f39c12;"></span><span style="font-size: 13px;">75th Percentile: ${stats.q75.toFixed(6)}</span></div>
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
                <div class="stat-item">
                    <div class="stat-label">Mean</div>
                    <div class="stat-value">${stats.mean.toFixed(6)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Median</div>
                    <div class="stat-value">${stats.median.toFixed(6)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Std Dev</div>
                    <div class="stat-value">${stats.std.toFixed(6)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">25th Percentile</div>
                    <div class="stat-value">${stats.q25.toFixed(6)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">75th Percentile</div>
                    <div class="stat-value">${stats.q75.toFixed(6)}</div>
                </div>
                ${ovcLegendHTML}
                ${statsLegendHTML}
            `;

            // Destroy existing chart if it exists
            if (window.rateChartInstance) {
                window.rateChartInstance.destroy();
            }

            // Create chart
            const ctx = document.getElementById('rateChart').getContext('2d');

            // Inline plugin that draws vertical OVC marker lines.
            // The x-axis is a category axis, so we convert each rate to a pixel
            // position using the spacing between category ticks.
            const ovcMarkerPlugin = {
                id: 'ovcMarkers',
                afterDatasetsDraw(chart) {
                    const xAxis = chart.scales.x;
                    const yAxis = chart.scales.y;
                    // Pixel centers of bin 0 and bin 1 give us pixels-per-bin.
                    const x0 = xAxis.getPixelForTick(0);
                    const x1 = xAxis.getPixelForTick(1);
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

                    // Draw statistical lines
                    drawLine(stats.mean, '#e74c3c', false);      // Mean - red solid
                    drawLine(stats.median, '#3498db', false);    // Median - blue solid
                    drawLine(stats.q25, '#f39c12', true);         // 25th percentile - orange dotted
                    drawLine(stats.q75, '#f39c12', true);         // 75th percentile - orange dotted

                    // Draw OVC lines on top
                    if (ovc2025) drawLine(ovc2025.max_local_rate, '#9b59b6', true);
                    if (ovcProposed) drawLine(ovcProposed.max_local_rate, '#28a745', true);
                }
            };

            window.rateChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: binLabels,
                    datasets: [{
                        label: 'Number of Cities',
                        data: bins,
                        backgroundColor: 'rgba(0, 102, 204, 0.7)',
                        borderColor: 'rgba(0, 102, 204, 1)',
                        borderWidth: 1
                    }]
                },
                plugins: [ovcMarkerPlugin],
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Distribution of Max Local-ish Tax Rates',
                            font: { size: 16 }
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
output_path = Path("city_tax_burden.html")
with open(output_path, 'w') as f:
    f.write(html_content)

print(f"Generated {output_path}")
