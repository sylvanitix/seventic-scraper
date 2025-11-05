// Lead Scraper Pro - Modern UI

let currentJobId = null;
let pollInterval = null;

// Pipeline data stored in memory
const pipelineData = {
    companies: [],
    domains: [],
    enriched: []
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Lead Scraper Pro loaded');
});

// Step Navigation
function goToStep(stepNumber) {
    // Hide all steps
    document.querySelectorAll('.step-content').forEach(el => el.style.display = 'none');

    // Show target step
    document.getElementById(`step-${stepNumber}`).style.display = 'block';

    // Update step indicators
    document.querySelectorAll('.step').forEach((step, index) => {
        const num = index + 1;
        step.classList.remove('active', 'completed');

        if (num < stepNumber) {
            step.classList.add('completed');
        } else if (num === stepNumber) {
            step.classList.add('active');
        }
    });

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Update info boxes
    if (stepNumber === 2) {
        const count = pipelineData.companies.length;
        document.getElementById('domain-info-count').textContent = `${count} entreprises`;
    } else if (stepNumber === 3) {
        const count = pipelineData.domains.filter(d => d.domain).length;
        document.getElementById('enrich-info-count').textContent = `${count} entreprises`;
    }
}

// Step 1: Scraping
async function startScraping() {
    const url = document.getElementById('scraper-url').value.trim();
    const maxPages = parseInt(document.getElementById('scraper-pages').value);

    if (!url) {
        alert('Veuillez entrer une URL');
        return;
    }

    try {
        showProgress('Scraping en cours...');

        const response = await fetch('/api/scrape-universal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, max_pages: maxPages })
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            hideProgress();
            return;
        }

        currentJobId = data.job_id;
        startPolling(handleScrapingComplete);

    } catch (error) {
        alert('Erreur: ' + error.message);
        hideProgress();
    }
}

function handleScrapingComplete(job) {
    hideProgress();

    if (job.status === 'failed') {
        alert('Erreur: ' + job.error);
        return;
    }

    // Store data
    pipelineData.companies = job.data || [];

    // Show results
    const count = pipelineData.companies.length;
    document.getElementById('scraper-count').textContent = `${count} entreprises`;

    // Preview (first 10)
    const previewHtml = pipelineData.companies.slice(0, 10).map((company, index) => `
        <div class="preview-item">
            <div>
                <div class="preview-item-name">${index + 1}. ${company.name}</div>
            </div>
        </div>
    `).join('');

    document.getElementById('scraper-preview').innerHTML = previewHtml +
        (count > 10 ? `<div class="preview-item"><div class="preview-item-meta">... et ${count - 10} autres</div></div>` : '');

    document.getElementById('scraper-results').style.display = 'block';
}

// Step 2: Domain Finding
async function startDomainFinder() {
    if (pipelineData.companies.length === 0) {
        alert('Aucune entreprise à traiter');
        return;
    }

    try {
        showProgress('Recherche de domaines...');

        const response = await fetch('/api/find-domains', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            hideProgress();
            return;
        }

        currentJobId = data.job_id;
        startPolling(handleDomainComplete);

    } catch (error) {
        alert('Erreur: ' + error.message);
        hideProgress();
    }
}

function handleDomainComplete(job) {
    hideProgress();

    if (job.status === 'failed') {
        alert('Erreur: ' + job.error);
        return;
    }

    // Store data
    pipelineData.domains = job.data || [];

    // Show results
    const found = pipelineData.domains.filter(d => d.domain).length;
    document.getElementById('domain-count').textContent = `${found} domaines`;

    // Preview (first 10 with domains)
    const withDomains = pipelineData.domains.filter(d => d.domain).slice(0, 10);
    const previewHtml = withDomains.map((item, index) => {
        const confidence = Math.round((item.confidence_score || 0) * 100);
        const badgeColor = confidence >= 70 ? '#dcfce7' : '#fef3c7';
        const textColor = confidence >= 70 ? '#166534' : '#92400e';

        return `
            <div class="preview-item">
                <div>
                    <div class="preview-item-name">${index + 1}. ${item.company_name}</div>
                    <div class="preview-item-meta">${item.domain}</div>
                </div>
                <span class="preview-item-badge" style="background: ${badgeColor}; color: ${textColor}">
                    ${confidence}%
                </span>
            </div>
        `;
    }).join('');

    document.getElementById('domain-preview').innerHTML = previewHtml +
        (found > 10 ? `<div class="preview-item"><div class="preview-item-meta">... et ${found - 10} autres</div></div>` : '');

    document.getElementById('domain-results').style.display = 'block';
}

// Step 3: Enrichment
async function startEnrichment() {
    const withDomains = pipelineData.domains.filter(d => d.domain);

    if (withDomains.length === 0) {
        alert('Aucun domaine trouvé');
        return;
    }

    try {
        showProgress('Enrichissement en cours...');

        const response = await fetch('/api/enrich', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
            hideProgress();
            return;
        }

        currentJobId = data.job_id;
        startPolling(handleEnrichmentComplete);

    } catch (error) {
        alert('Erreur: ' + error.message);
        hideProgress();
    }
}

function handleEnrichmentComplete(job) {
    hideProgress();

    if (job.status === 'failed') {
        alert('Erreur: ' + job.error);
        return;
    }

    // Store data
    pipelineData.enriched = job.data || [];

    // Show stats
    const count = pipelineData.enriched.length;
    const emails = pipelineData.enriched.filter(c => c.company_email).length;
    const phones = pipelineData.enriched.filter(c => c.company_phone).length;
    const linkedin = pipelineData.enriched.filter(c => c.company_linkedin).length;

    document.getElementById('enrich-count').textContent = `${count} entreprises`;
    document.getElementById('stat-emails').textContent = emails;
    document.getElementById('stat-phones').textContent = phones;
    document.getElementById('stat-linkedin').textContent = linkedin;

    // Preview (first 10)
    const previewHtml = pipelineData.enriched.slice(0, 10).map((company, index) => {
        const contacts = [];
        if (company.company_email) contacts.push('📧');
        if (company.company_phone) contacts.push('📞');
        if (company.company_linkedin) contacts.push('💼');

        return `
            <div class="preview-item">
                <div>
                    <div class="preview-item-name">${index + 1}. ${company.company_name}</div>
                    <div class="preview-item-meta">
                        ${company.domain}
                        ${contacts.length > 0 ? ' • ' + contacts.join(' ') : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    document.getElementById('enrich-preview').innerHTML = previewHtml +
        (count > 10 ? `<div class="preview-item"><div class="preview-item-meta">... et ${count - 10} autres</div></div>` : '');

    document.getElementById('enrich-results').style.display = 'block';
}

// Export Data
async function exportData(stage, format) {
    const stageMap = {
        'companies': 'companies',
        'domains': 'domains',
        'enriched': 'enriched'
    };

    const actualStage = stageMap[stage];

    try {
        const response = await fetch(`/api/export/${actualStage}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ format })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${stage}_${new Date().toISOString().split('T')[0]}.${format}`;
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

// Polling
function startPolling(onComplete) {
    stopPolling();

    pollInterval = setInterval(async () => {
        if (!currentJobId) return;

        try {
            const response = await fetch(`/api/jobs/${currentJobId}`);
            const job = await response.json();

            // Update progress
            if (job.total > 0) {
                updateProgress(job.progress, job.total, job.current_item);
            }

            // Check if complete
            if (job.status === 'completed' || job.status === 'failed') {
                stopPolling();
                if (onComplete) {
                    onComplete(job);
                }
                currentJobId = null;
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 1000);
}

function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// Config Modal
function showConfig() {
    loadConfigValues();
    document.getElementById('config-modal').style.display = 'flex';
}

function closeConfig() {
    document.getElementById('config-modal').style.display = 'none';
}

async function loadConfigValues() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        // Load values if API returns them
    } catch (error) {
        console.error('Config load error:', error);
    }
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
