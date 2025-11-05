// Web Scraper Pro - Client-side JavaScript

let currentJobId = null;
let pollInterval = null;

// Load stats on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadApiStatus();
    setInterval(loadStats, 5000); // Update stats every 5 seconds
});

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        document.getElementById('stat-companies').textContent = stats.total_companies || '-';
        document.getElementById('stat-domains').textContent = stats.domains_found || '-';
        document.getElementById('stat-emails').textContent = stats.emails_found || '-';
        document.getElementById('stat-jobs').textContent = stats.active_jobs || '0';
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load API configuration status
async function loadApiStatus() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        const statusHtml = `
            <div style="display: flex; gap: 10px; flex-direction: column;">
                <div>
                    <strong>Pappers API:</strong>
                    <span style="color: ${config.pappers_configured ? '#10b981' : '#ef4444'}">
                        ${config.pappers_configured ? '✓ Configuré' : '✗ Non configuré'}
                    </span>
                </div>
                <div>
                    <strong>Hunter API:</strong>
                    <span style="color: ${config.hunter_configured ? '#10b981' : '#ef4444'}">
                        ${config.hunter_configured ? '✓ Configuré' : '✗ Non configuré'}
                    </span>
                </div>
            </div>
        `;

        document.getElementById('api-status').innerHTML = statusHtml;
    } catch (error) {
        console.error('Error loading API status:', error);
    }
}

// Run Full Pipeline (NEW!)
async function runFullPipeline() {
    if (currentJobId) {
        alert('Un job est déjà en cours. Veuillez attendre qu\'il se termine.');
        return;
    }

    const url = document.getElementById('pipeline-url').value.trim();
    const maxPages = parseInt(document.getElementById('pipeline-pages').value);

    if (!url) {
        alert('Veuillez entrer une URL valide');
        return;
    }

    if (!confirm(`Lancer le pipeline complet pour ${url} ?\n\nCela va :\n- Scraper jusqu'à ${maxPages} pages\n- Trouver les domaines\n- Enrichir les données\n\nCela peut prendre 10-30 minutes selon le nombre d'entreprises.`)) {
        return;
    }

    try {
        const response = await fetch('/api/full-pipeline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                max_pages: maxPages
            })
        });

        const data = await response.json();

        if (data.error) {
            alert('Erreur: ' + data.error);
            return;
        }

        currentJobId = data.job_id;

        showProgress('Pipeline complet en cours...');
        startPolling();
    } catch (error) {
        alert('Erreur lors du lancement du pipeline: ' + error.message);
    }
}

// Run Scraping
async function runScraping() {
    if (currentJobId) {
        alert('Un job est déjà en cours. Veuillez attendre qu\'il se termine.');
        return;
    }

    if (!confirm('Lancer le scraping du site Equipauto ? Cela peut prendre quelques minutes.')) {
        return;
    }

    try {
        const response = await fetch('/api/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();
        currentJobId = data.job_id;

        showProgress('Scraping en cours...');
        startPolling();
    } catch (error) {
        alert('Erreur lors du lancement du scraping: ' + error.message);
    }
}

// Run Domain Finder
async function runDomainFinder() {
    if (currentJobId) {
        alert('Un job est déjà en cours. Veuillez attendre qu\'il se termine.');
        return;
    }

    const limit = document.getElementById('domain-limit').value;
    const limitText = limit ? `${limit} entreprises` : 'toutes les entreprises';

    if (!confirm(`Lancer la recherche de domaines pour ${limitText} ?`)) {
        return;
    }

    try {
        const response = await fetch('/api/find-domains', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                max_results: limit ? parseInt(limit) : null
            })
        });

        const data = await response.json();
        currentJobId = data.job_id;

        showProgress('Recherche de domaines en cours...');
        startPolling();
    } catch (error) {
        alert('Erreur lors du lancement de la recherche: ' + error.message);
    }
}

// Run Enrichment
async function runEnrichment() {
    if (currentJobId) {
        alert('Un job est déjà en cours. Veuillez attendre qu\'il se termine.');
        return;
    }

    const limit = document.getElementById('enrich-limit').value;
    const limitText = limit ? `${limit} entreprises` : 'toutes les entreprises';

    if (!confirm(`Lancer l'enrichissement pour ${limitText} ?`)) {
        return;
    }

    try {
        const response = await fetch('/api/enrich', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                max_results: limit ? parseInt(limit) : null
            })
        });

        const data = await response.json();
        currentJobId = data.job_id;

        showProgress('Enrichissement en cours...');
        startPolling();
    } catch (error) {
        alert('Erreur lors du lancement de l\'enrichissement: ' + error.message);
    }
}

// Show progress section
function showProgress(title) {
    document.getElementById('progress-title').textContent = title;
    document.getElementById('progress-section').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-text').textContent = '0%';
    document.getElementById('progress-current').textContent = 'Initialisation...';
    document.getElementById('progress-count').textContent = '0 / 0';
    document.getElementById('progress-logs').innerHTML = '';
}

// Close progress
function closeProgress() {
    document.getElementById('progress-section').style.display = 'none';
    stopPolling();
}

// Close results
function closeResults() {
    document.getElementById('results-section').style.display = 'none';
}

// Start polling for job status
function startPolling() {
    stopPolling(); // Clear any existing interval

    pollInterval = setInterval(async () => {
        if (!currentJobId) return;

        try {
            const response = await fetch(`/api/jobs/${currentJobId}`);
            const job = await response.json();

            updateProgress(job);

            if (job.status === 'completed' || job.status === 'failed') {
                stopPolling();
                showResults(job);
                currentJobId = null;
            }
        } catch (error) {
            console.error('Error polling job status:', error);
        }
    }, 1000); // Poll every second
}

// Stop polling
function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// Update progress display
function updateProgress(job) {
    const percentage = job.total > 0 ? Math.round((job.progress / job.total) * 100) : 0;

    document.getElementById('progress-bar').style.width = percentage + '%';
    document.getElementById('progress-text').textContent = percentage + '%';
    document.getElementById('progress-current').textContent = job.current_item || 'En cours...';
    document.getElementById('progress-count').textContent = `${job.progress} / ${job.total}`;

    // Update logs
    if (job.logs && job.logs.length > 0) {
        const logsHtml = job.logs.map(log => {
            const className = log.level === 'error' ? 'log-error' : '';
            return `<div class="log-entry ${className}">[${new Date(log.timestamp).toLocaleTimeString()}] ${log.message}</div>`;
        }).join('');

        document.getElementById('progress-logs').innerHTML = logsHtml;

        // Auto-scroll to bottom
        const logsElement = document.getElementById('progress-logs');
        logsElement.scrollTop = logsElement.scrollHeight;
    }
}

// Show results
function showResults(job) {
    document.getElementById('progress-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'block';

    let resultsHtml = '';

    if (job.status === 'failed') {
        resultsHtml = `
            <div style="color: #ef4444; padding: 20px; background: #fee2e2; border-radius: 8px;">
                <h4>❌ Erreur</h4>
                <p>${job.error}</p>
            </div>
        `;
    } else {
        // Success
        const results = job.results;

        if (job.job_type === 'full_pipeline') {
            resultsHtml = `
                <div class="result-success">
                    <h4>✅ Pipeline Complet Terminé !</h4>
                </div>
                <div class="result-stat">
                    <span>Entreprises scrapées:</span>
                    <strong>${results.total_companies || 0}</strong>
                </div>
                <div class="result-stat">
                    <span>Domaines trouvés:</span>
                    <strong>${results.domains_found || 0} (${results.total_companies ? Math.round((results.domains_found / results.total_companies) * 100) : 0}%)</strong>
                </div>
                <div class="result-stat">
                    <span>Entreprises enrichies:</span>
                    <strong>${results.companies_enriched || 0}</strong>
                </div>
                <div class="result-stat">
                    <span>Emails trouvés:</span>
                    <strong>${results.emails_found || 0} (${results.companies_enriched ? Math.round((results.emails_found / results.companies_enriched) * 100) : 0}%)</strong>
                </div>
                <div class="result-stat">
                    <span>Téléphones trouvés:</span>
                    <strong>${results.phones_found || 0} (${results.companies_enriched ? Math.round((results.phones_found / results.companies_enriched) * 100) : 0}%)</strong>
                </div>
                <div class="result-stat">
                    <span>LinkedIn trouvés:</span>
                    <strong>${results.linkedin_found || 0} (${results.companies_enriched ? Math.round((results.linkedin_found / results.companies_enriched) * 100) : 0}%)</strong>
                </div>
                <div class="result-stat">
                    <span>Temps total:</span>
                    <strong>${Math.round(results.total_time || 0)}s (${Math.round((results.total_time || 0) / 60)}min)</strong>
                </div>
                <div class="download-section">
                    <h4>📥 Télécharger les résultats</h4>
                    <div class="download-buttons">
                        <button class="btn btn-download" onclick="downloadPipelineResults('csv')">
                            📄 CSV
                        </button>
                        <button class="btn btn-download" onclick="downloadPipelineResults('xlsx')">
                            📊 Excel
                        </button>
                        <button class="btn btn-download" onclick="downloadPipelineResults('json')">
                            📋 JSON
                        </button>
                    </div>
                </div>
            `;
        } else if (job.job_type === 'scraping') {
            resultsHtml = `
                <div class="result-stat">
                    <span>Entreprises scrapées:</span>
                    <strong>${results.total_scraped || 0}</strong>
                </div>
                <div class="result-stat">
                    <span>Entreprises uniques:</span>
                    <strong>${results.unique_companies || 0}</strong>
                </div>
            `;
        } else if (job.job_type === 'domain_finding') {
            resultsHtml = `
                <div class="result-stat">
                    <span>Entreprises traitées:</span>
                    <strong>${results.total_processed || 0}</strong>
                </div>
                <div class="result-stat">
                    <span>Domaines trouvés:</span>
                    <strong>${results.domains_found || 0}</strong>
                </div>
                <div class="result-stat">
                    <span>Non trouvés:</span>
                    <strong>${results.not_found || 0}</strong>
                </div>
                <div class="result-stat">
                    <span>Taux de réussite:</span>
                    <strong>${Math.round((results.domains_found / results.total_processed) * 100)}%</strong>
                </div>
            `;
        } else if (job.job_type === 'enrichment') {
            resultsHtml = `
                <div class="result-stat">
                    <span>Entreprises traitées:</span>
                    <strong>${results.total_processed || 0}</strong>
                </div>
                <div class="result-stat">
                    <span>Emails trouvés:</span>
                    <strong>${results.emails_found || 0} (${Math.round((results.emails_found / results.total_processed) * 100)}%)</strong>
                </div>
                <div class="result-stat">
                    <span>Téléphones trouvés:</span>
                    <strong>${results.phones_found || 0} (${Math.round((results.phones_found / results.total_processed) * 100)}%)</strong>
                </div>
                <div class="result-stat">
                    <span>LinkedIn trouvés:</span>
                    <strong>${results.linkedin_found || 0} (${Math.round((results.linkedin_found / results.total_processed) * 100)}%)</strong>
                </div>
            `;
        }

        // Add download links
        if (results.files && results.files.length > 0) {
            resultsHtml += `
                <div class="download-section">
                    <h4>📥 Télécharger les résultats</h4>
                    <div class="download-links">
                        ${results.files.map(file => `
                            <a href="/api/download/${file}" class="download-link" download>
                                ${file}
                            </a>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    }

    document.getElementById('results-body').innerHTML = resultsHtml;

    // Reload stats
    loadStats();
}

// Show configuration modal
function showConfig() {
    loadConfigValues();
    document.getElementById('config-modal').style.display = 'flex';
}

// Close configuration modal
function closeConfig() {
    document.getElementById('config-modal').style.display = 'none';
}

// Load configuration values
async function loadConfigValues() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        document.getElementById('pappers-key').value = config.pappers_api_key || '';
        document.getElementById('hunter-key').value = config.hunter_api_key || '';
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Save configuration
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
            alert('Configuration sauvegardée avec succès !');
            closeConfig();
            loadApiStatus();
        } else {
            alert('Erreur lors de la sauvegarde de la configuration');
        }
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Download pipeline results
async function downloadPipelineResults(format) {
    try {
        const response = await fetch('/api/export/enriched', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ format: format })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `leads_${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Erreur lors du téléchargement');
        }
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('config-modal');
    if (event.target === modal) {
        closeConfig();
    }
}
