// Supervised Scraper - Smart Pattern Detection

let analysisResult = null;
let selectedPattern = 0;
let scrapedData = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Supervised Scraper loaded');
});

// Step 1: Analyze URL
async function analyzeUrl() {
    const url = document.getElementById('analyze-url').value.trim();

    if (!url) {
        alert('Veuillez entrer une URL');
        return;
    }

    try {
        showProgress('Analyse de la page en cours...');

        const response = await fetch('/api/analyze-patterns', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        hideProgress();

        if (!data.success) {
            alert('Erreur: ' + (data.error || 'Aucun pattern détecté'));
            return;
        }

        // Store result
        analysisResult = data;

        // Show mapping step
        displayPatterns(data.patterns);
        document.getElementById('step-analyze').style.display = 'none';
        document.getElementById('step-mapping').style.display = 'block';

    } catch (error) {
        hideProgress();
        alert('Erreur: ' + error.message);
    }
}

// Display detected patterns
function displayPatterns(patterns) {
    const container = document.getElementById('pattern-selector');

    if (!patterns || patterns.length === 0) {
        container.innerHTML = '<p>Aucun pattern détecté</p>';
        return;
    }

    container.innerHTML = '<h4 style="margin-bottom: 1rem;">Patterns détectés (' + patterns.length + ')</h4>';

    patterns.forEach((pattern, index) => {
        const card = document.createElement('div');
        card.className = 'pattern-card' + (index === 0 ? ' selected' : '');
        card.onclick = () => selectPattern(index);

        const columnsHtml = pattern.columns
            .filter(col => col.type === 'text' || col.type === 'url')
            .slice(0, 5)
            .map(col => `<span class="column-tag ${col.type}">${col.name}</span>`)
            .join('');

        card.innerHTML = `
            <div class="pattern-header">
                <div class="pattern-title">Pattern #${index + 1}: ${pattern.signature}</div>
                <span class="pattern-count">${pattern.count} items</span>
            </div>
            <div class="pattern-columns">
                ${columnsHtml}
                ${pattern.columns.length > 5 ? '<span class="column-tag">+' + (pattern.columns.length - 5) + ' autres</span>' : ''}
            </div>
        `;

        container.appendChild(card);
    });

    // Show first pattern by default
    selectPattern(0);
}

// Select a pattern
function selectPattern(index) {
    selectedPattern = index;

    // Update UI
    document.querySelectorAll('.pattern-card').forEach((card, i) => {
        if (i === index) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });

    // Show column mapping for this pattern
    displayColumnMapping(analysisResult.patterns[index]);
}

// Display column mapping interface
function displayColumnMapping(pattern) {
    const mappingDiv = document.getElementById('column-mapping');
    mappingDiv.style.display = 'block';

    // Populate column selector
    const columnSelect = document.getElementById('company-column');
    columnSelect.innerHTML = '';

    // Add text columns first (most likely to contain company names)
    const textColumns = pattern.columns.filter(col => col.type === 'text');
    const otherColumns = pattern.columns.filter(col => col.type !== 'text');

    [...textColumns, ...otherColumns].forEach(col => {
        const option = document.createElement('option');
        option.value = col.name;
        option.textContent = `${col.name} (${col.type}) - ${col.presence.toFixed(0)}%`;
        columnSelect.appendChild(option);
    });

    // Display preview table
    displayPreviewTable(pattern);

    // Update preview when column selection changes
    columnSelect.onchange = () => displayPreviewTable(pattern);
}

// Display preview table
function displayPreviewTable(pattern) {
    const table = document.getElementById('preview-table');
    const selectedColumn = document.getElementById('company-column').value;

    if (!pattern.preview || pattern.preview.length === 0) {
        table.innerHTML = '<tr><td>Aucune donnée à afficher</td></tr>';
        return;
    }

    // Get all unique columns from preview data
    const allColumns = new Set();
    pattern.preview.forEach(item => {
        Object.keys(item).forEach(key => allColumns.add(key));
    });

    // Build table header
    let html = '<thead><tr>';
    allColumns.forEach(col => {
        const isSelected = col === selectedColumn;
        html += `<th${isSelected ? ' style="background: #fef3c7;"' : ''}>${col}${isSelected ? ' 🎯' : ''}</th>`;
    });
    html += '</tr></thead><tbody>';

    // Build table rows (max 10 for preview)
    pattern.preview.slice(0, 10).forEach(item => {
        html += '<tr>';
        allColumns.forEach(col => {
            const value = item[col] || '-';
            const isSelected = col === selectedColumn;
            const displayValue = typeof value === 'string' && value.length > 50
                ? value.substring(0, 50) + '...'
                : value;

            html += `<td${isSelected ? ' class="highlight"' : ''}>${displayValue}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody>';
    table.innerHTML = html;
}

// Step 2: Start supervised scraping
async function startSupervisedScraping() {
    const url = document.getElementById('analyze-url').value.trim();
    const maxPages = parseInt(document.getElementById('supervised-pages').value);
    const companyColumn = document.getElementById('company-column').value;

    // Récupère la signature du pattern sélectionné
    const patternSignature = analysisResult.patterns[selectedPattern].signature;

    try {
        showProgress('Scraping en cours...');

        const response = await fetch('/api/scrape-supervised', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url,
                pattern_signature: patternSignature,  // IMPORTANT: signature au lieu d'index
                pattern_index: selectedPattern,  // Gardé pour fallback
                company_column: companyColumn,
                max_pages: maxPages
            })
        });

        const data = await response.json();

        if (data.error) {
            hideProgress();
            alert(data.error);
            return;
        }

        // Poll for results
        pollJobStatus(data.job_id, handleScrapingComplete);

    } catch (error) {
        hideProgress();
        alert('Erreur: ' + error.message);
    }
}

// Handle scraping completion
function handleScrapingComplete(job) {
    hideProgress();

    if (job.status === 'failed') {
        alert('Erreur: ' + job.error);
        return;
    }

    // Store data
    scrapedData = job.data || [];

    // Display results
    displayResults(scrapedData);

    // Hide mapping, show results
    document.getElementById('step-mapping').style.display = 'none';
    document.getElementById('step-results').style.display = 'block';
}

// Display scraping results
function displayResults(companies) {
    document.getElementById('result-count').textContent = `${companies.length} entreprises`;

    const previewHtml = companies.slice(0, 20).map((company, index) => {
        const hasUrl = company.url && company.url !== '';

        return `
            <div class="preview-item">
                <div>
                    <div class="preview-item-name">${index + 1}. ${company.name}</div>
                    ${hasUrl ? `<div class="preview-item-meta">🔗 ${company.url}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');

    document.getElementById('result-preview').innerHTML = previewHtml +
        (companies.length > 20 ? `<div class="preview-item"><div class="preview-item-meta">... et ${companies.length - 20} autres</div></div>` : '');
}

// Export data
async function exportData(format) {
    if (scrapedData.length === 0) {
        alert('Aucune donnée à exporter');
        return;
    }

    try {
        const response = await fetch('/api/export-direct', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                data: scrapedData,
                format: format
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `companies_${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Erreur lors de l\'export');
        }
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Continue to domain finding
function continueToNextSteps() {
    // Store companies in pipeline and redirect to step 2
    window.location.href = '/?step=2&companies=' + encodeURIComponent(JSON.stringify(scrapedData));
}

// Navigation
function goBackToAnalyze() {
    document.getElementById('step-mapping').style.display = 'none';
    document.getElementById('step-analyze').style.display = 'block';
}

function startNewScraping() {
    document.getElementById('step-results').style.display = 'none';
    document.getElementById('step-analyze').style.display = 'block';
    scrapedData = [];
    analysisResult = null;
}

// Progress Modal
function showProgress(title) {
    document.getElementById('progress-title').textContent = title;
    document.getElementById('progress-fill').style.width = '0%';
    document.getElementById('progress-text').textContent = '0%';
    document.getElementById('progress-details').textContent = 'Initialisation...';
    document.getElementById('progress-modal').style.display = 'flex';
}

function hideProgress() {
    document.getElementById('progress-modal').style.display = 'none';
}

function updateProgress(current, total, message) {
    const percent = total > 0 ? Math.round((current / total) * 100) : 0;
    document.getElementById('progress-fill').style.width = percent + '%';
    document.getElementById('progress-text').textContent = percent + '%';
    document.getElementById('progress-details').textContent = message || `${current} / ${total}`;
}

// Job Polling
function pollJobStatus(jobId, onComplete) {
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/jobs/${jobId}`);
            const job = await response.json();

            // Update progress
            if (job.total > 0) {
                updateProgress(job.progress, job.total, job.current_item);
            }

            // Check if complete
            if (job.status === 'completed' || job.status === 'failed') {
                clearInterval(pollInterval);
                if (onComplete) {
                    onComplete(job);
                }
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 1000);
}

// Config Modal
function showConfig() {
    document.getElementById('config-modal').style.display = 'flex';
}

function closeConfig() {
    document.getElementById('config-modal').style.display = 'none';
}

async function saveConfig() {
    const pappersKey = document.getElementById('pappers-key').value;
    const hunterKey = document.getElementById('hunter-key').value;

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                pappers_api_key: pappersKey,
                hunter_api_key: hunterKey
            })
        });

        if (response.ok) {
            alert('Configuration sauvegardée !');
            closeConfig();
        } else {
            alert('Erreur lors de la sauvegarde');
        }
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Close modal on click outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}
