// Modern Lead Scraper - Complete Pipeline Flow

// Global state
const pipeline = {
    companies: [],
    domains: [],
    enriched: []
};

let analysisResult = null;
let selectedPattern = 0;
let currentJobId = null;
let pollInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Lead Scraper Pro - Modern UI loaded');
    updateBadges();
    updateNavigationState();
});

//===========================================
// NAVIGATION
//===========================================

function showStep(step) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(el => {
        el.classList.remove('active');
    });

    // Show target section
    document.getElementById(`section-${step}`).classList.add('active');

    // Update nav menu
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-step="${step}"]`).classList.add('active');

    // Update header
    const titles = {
        'scraping': {
            title: 'Scraping d\'entreprises',
            subtitle: 'Analysez et extrayez les données d\'entreprises'
        },
        'domains': {
            title: 'Recherche de domaines',
            subtitle: 'Trouvez automatiquement les sites web'
        },
        'enrichment': {
            title: 'Enrichissement des données',
            subtitle: 'Extraction d\'emails, téléphones et LinkedIn'
        }
    };

    document.getElementById('page-title').textContent = titles[step].title;
    document.getElementById('page-subtitle').textContent = titles[step].subtitle;

    // Update progress indicators
    updateProgressIndicators(step);

    // Update step data
    if (step === 'domains') {
        updateDomainsStep();
    } else if (step === 'enrichment') {
        updateEnrichmentStep();
    }
}

function updateProgressIndicators(currentStep) {
    const steps = ['scraping', 'domains', 'enrichment'];
    const currentIndex = steps.indexOf(currentStep);

    steps.forEach((step, index) => {
        const el = document.getElementById(`progress-${step}`);
        el.classList.remove('active', 'completed');

        if (index < currentIndex) {
            el.classList.add('completed');
        } else if (index === currentIndex) {
            el.classList.add('active');
        }
    });
}

function updateNavigationState() {
    // Enable/disable nav items based on data availability
    const hasCompanies = pipeline.companies.length > 0;
    const hasDomains = pipeline.domains.length > 0;

    const domainsNav = document.querySelector('[data-step="domains"]');
    const enrichmentNav = document.querySelector('[data-step="enrichment"]');

    if (!hasCompanies) {
        domainsNav.style.opacity = '0.5';
        domainsNav.style.pointerEvents = 'none';
    } else {
        domainsNav.style.opacity = '1';
        domainsNav.style.pointerEvents = 'auto';
    }

    if (!hasDomains) {
        enrichmentNav.style.opacity = '0.5';
        enrichmentNav.style.pointerEvents = 'none';
    } else {
        enrichmentNav.style.opacity = '1';
        enrichmentNav.style.pointerEvents = 'auto';
    }
}

function updateBadges() {
    document.getElementById('badge-scraping').textContent = pipeline.companies.length;
    document.getElementById('badge-domains').textContent = pipeline.domains.filter(d => d.domain).length;
    document.getElementById('badge-enrichment').textContent = pipeline.enriched.length;
}

//===========================================
// STEP 1: SCRAPING
//===========================================

async function analyzeUrl() {
    const url = document.getElementById('scrape-url').value.trim();

    if (!url) {
        alert('Veuillez entrer une URL');
        return;
    }

    try {
        showModal('Analyse de la page...', 'Détection des patterns en cours');

        const response = await fetch('/api/analyze-patterns', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        hideModal();

        if (!data.success) {
            alert('Erreur: ' + (data.error || 'Aucun pattern détecté'));
            return;
        }

        analysisResult = data;
        displayPatterns(data.patterns);

    } catch (error) {
        hideModal();
        alert('Erreur: ' + error.message);
    }
}

function displayPatterns(patterns) {
    const container = document.getElementById('pattern-list');
    const panel = document.getElementById('pattern-panel');

    if (!patterns || patterns.length === 0) {
        container.innerHTML = '<p>Aucun pattern détecté</p>';
        return;
    }

    panel.style.display = 'block';

    container.innerHTML = patterns.map((pattern, index) => {
        const textCols = pattern.columns.filter(c => c.type === 'text').slice(0, 3);
        return `
            <div class="pattern-card ${index === 0 ? 'selected' : ''}" onclick="selectPattern(${index})">
                <div class="pattern-header">
                    <div class="pattern-title">Pattern #${index + 1}: ${pattern.signature}</div>
                    <span class="pattern-count">${pattern.count} items</span>
                </div>
                <div class="pattern-columns">
                    ${textCols.map(col => `<span class="column-tag text">${col.name}</span>`).join('')}
                    ${pattern.columns.length > 3 ? `<span class="column-tag">+${pattern.columns.length - 3}</span>` : ''}
                </div>
            </div>
        `;
    }).join('');

    selectPattern(0);
}

function selectPattern(index) {
    selectedPattern = index;

    document.querySelectorAll('.pattern-card').forEach((card, i) => {
        card.classList.toggle('selected', i === index);
    });

    displayColumnMapping(analysisResult.patterns[index]);
}

function displayColumnMapping(pattern) {
    const mappingPanel = document.getElementById('mapping-panel');
    mappingPanel.style.display = 'block';

    const columnSelect = document.getElementById('company-column');
    columnSelect.innerHTML = '';

    const textColumns = pattern.columns.filter(c => c.type === 'text');
    const otherColumns = pattern.columns.filter(c => c.type !== 'text');

    [...textColumns, ...otherColumns].forEach(col => {
        const option = document.createElement('option');
        option.value = col.name;
        option.textContent = `${col.name} (${col.type}) - ${col.presence.toFixed(0)}%`;
        columnSelect.appendChild(option);
    });

    displayPreviewTable(pattern);
    columnSelect.onchange = () => displayPreviewTable(pattern);
}

function displayPreviewTable(pattern) {
    const table = document.getElementById('preview-table');
    const selectedColumn = document.getElementById('company-column').value;

    if (!pattern.preview || pattern.preview.length === 0) {
        table.innerHTML = '<tr><td>Aucune donnée</td></tr>';
        return;
    }

    const allColumns = new Set();
    pattern.preview.forEach(item => {
        Object.keys(item).forEach(key => allColumns.add(key));
    });

    let html = '<thead><tr>';
    allColumns.forEach(col => {
        const isSelected = col === selectedColumn;
        html += `<th${isSelected ? ' style="background: #fef3c7;"' : ''}>${col}${isSelected ? ' 🎯' : ''}</th>`;
    });
    html += '</tr></thead><tbody>';

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

async function startScraping() {
    const url = document.getElementById('scrape-url').value.trim();
    const maxPages = parseInt(document.getElementById('max-pages').value);
    const companyColumn = document.getElementById('company-column').value;
    const patternSignature = analysisResult.patterns[selectedPattern].signature;

    try {
        showModal('Scraping en cours...', 'Extraction des entreprises');

        const response = await fetch('/api/scrape-supervised', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url,
                pattern_signature: patternSignature,
                pattern_index: selectedPattern,
                company_column: companyColumn,
                max_pages: maxPages
            })
        });

        const data = await response.json();

        if (data.error) {
            hideModal();
            alert(data.error);
            return;
        }

        currentJobId = data.job_id;
        pollJob(handleScrapingComplete);

    } catch (error) {
        hideModal();
        alert('Erreur: ' + error.message);
    }
}

function handleScrapingComplete(job) {
    hideModal();

    if (job.status === 'failed') {
        alert('Erreur: ' + job.error);
        return;
    }

    // Store data
    pipeline.companies = job.data || [];
    updateBadges();
    updateNavigationState();

    // Show success and move to next step
    alert(`✅ ${pipeline.companies.length} entreprises extraites avec succès !`);
    showStep('domains');
}

//===========================================
// STEP 2: DOMAIN FINDER
//===========================================

function updateDomainsStep() {
    document.getElementById('domains-total').textContent = pipeline.companies.length;
    document.getElementById('domains-subtitle').textContent =
        `${pipeline.companies.length} entreprises prêtes pour la recherche de domaines`;
}

async function startDomainFinder() {
    if (pipeline.companies.length === 0) {
        alert('Aucune entreprise. Effectuez d\'abord le scraping.');
        return;
    }

    try {
        showModal('Recherche de domaines...', 'Analyse en cours');

        const response = await fetch('/api/find-domains', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.error) {
            hideModal();
            alert(data.error);
            return;
        }

        currentJobId = data.job_id;
        pollJob(handleDomainsComplete);

    } catch (error) {
        hideModal();
        alert('Erreur: ' + error.message);
    }
}

function handleDomainsComplete(job) {
    hideModal();

    if (job.status === 'failed') {
        alert('Erreur: ' + job.error);
        return;
    }

    pipeline.domains = job.data || [];
    updateBadges();
    updateNavigationState();

    const found = pipeline.domains.filter(d => d.domain).length;

    // Display results
    const list = document.getElementById('domains-list');
    list.innerHTML = pipeline.domains.filter(d => d.domain).slice(0, 20).map((item, i) => `
        <div class="result-item">
            <div>
                <div class="result-name">${item.company_name}</div>
                <div class="result-meta">${item.domain}</div>
            </div>
            <span class="result-badge">${Math.round((item.confidence_score || 0) * 100)}%</span>
        </div>
    `).join('');

    document.getElementById('domains-results').style.display = 'block';

    alert(`✅ ${found} domaines trouvés !`);
}

//===========================================
// STEP 3: ENRICHMENT
//===========================================

function updateEnrichmentStep() {
    const withDomains = pipeline.domains.filter(d => d.domain).length;
    document.getElementById('enrichment-total').textContent = withDomains;
    document.getElementById('enrichment-subtitle').textContent =
        `${withDomains} entreprises avec domaines prêtes pour l'enrichissement`;
}

async function startEnrichment() {
    const withDomains = pipeline.domains.filter(d => d.domain);

    if (withDomains.length === 0) {
        alert('Aucun domaine trouvé. Lancez d\'abord la recherche de domaines.');
        return;
    }

    try {
        showModal('Enrichissement...', 'Extraction des contacts');

        const response = await fetch('/api/enrich', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.error) {
            hideModal();
            alert(data.error);
            return;
        }

        currentJobId = data.job_id;
        pollJob(handleEnrichmentComplete);

    } catch (error) {
        hideModal();
        alert('Erreur: ' + error.message);
    }
}

function handleEnrichmentComplete(job) {
    hideModal();

    if (job.status === 'failed') {
        alert('Erreur: ' + job.error);
        return;
    }

    pipeline.enriched = job.data || [];
    updateBadges();

    // CASCADE: Display stats including companies without data
    const total = pipeline.enriched.length;
    const enriched = pipeline.enriched.filter(c => c.enrichment_status === 'enriched').length;
    const withoutDomains = pipeline.enriched.filter(c => c.enrichment_status === 'no_domain').length;
    const emails = pipeline.enriched.filter(c => c.company_email).length;
    const phones = pipeline.enriched.filter(c => c.company_phone).length;
    const linkedin = pipeline.enriched.filter(c => c.company_linkedin).length;

    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-emails').textContent = emails;
    document.getElementById('stat-phones').textContent = phones;
    document.getElementById('stat-linkedin').textContent = linkedin;

    // Display results - CASCADE: Montre TOUTES les entreprises
    const list = document.getElementById('enrichment-list');
    list.innerHTML = pipeline.enriched.slice(0, 30).map((company, i) => {
        const contacts = [];
        if (company.company_email) contacts.push('📧');
        if (company.company_phone) contacts.push('📞');
        if (company.company_linkedin) contacts.push('💼');

        const companyName = company.company_name || company.name || 'Unknown';
        const domain = company.domain || '❌ Pas de domaine';
        const contactInfo = contacts.length > 0 ? contacts.join(' ') : '⚠️ Pas de contacts';

        return `
            <div class="result-item">
                <div>
                    <div class="result-name">${companyName}</div>
                    <div class="result-meta">${domain} ${contactInfo}</div>
                </div>
            </div>
        `;
    }).join('');

    if (pipeline.enriched.length > 30) {
        list.innerHTML += `
            <div class="result-item" style="background: #f0f4ff; border-color: #6366f1;">
                <div class="result-name" style="color: #6366f1;">... et ${pipeline.enriched.length - 30} autres entreprises</div>
                <div class="result-meta">Exportez le CSV pour voir toutes les données</div>
            </div>
        `;
    }

    document.getElementById('enrichment-results').style.display = 'block';

    alert(`🎉 Pipeline terminé !\n\n✅ ${total} entreprises au total\n📊 ${enriched} enrichies\n🌐 ${emails} emails trouvés\n\nToutes les données (trouvées ou non) sont dans le CSV !`);
}

//===========================================
// EXPORT
//===========================================

async function exportData(stage, format) {
    try {
        const response = await fetch(`/api/export/${stage}`, {
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

//===========================================
// MODALS
//===========================================

function showModal(title, message) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-message').textContent = message;
    document.getElementById('modal-progress').style.width = '0%';
    document.getElementById('progress-modal').classList.add('show');
}

function hideModal() {
    document.getElementById('progress-modal').classList.remove('show');
}

function updateModalProgress(percent, message) {
    document.getElementById('modal-progress').style.width = percent + '%';
    if (message) {
        document.getElementById('modal-message').textContent = message;
    }
}

//===========================================
// JOB POLLING
//===========================================

function pollJob(onComplete) {
    if (pollInterval) clearInterval(pollInterval);

    pollInterval = setInterval(async () => {
        if (!currentJobId) return;

        try {
            const response = await fetch(`/api/jobs/${currentJobId}`);
            const job = await response.json();

            if (job.total > 0) {
                const percent = Math.round((job.progress / job.total) * 100);
                updateModalProgress(percent, job.current_item);
            }

            if (job.status === 'completed' || job.status === 'failed') {
                clearInterval(pollInterval);
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

//===========================================
// CONFIG
//===========================================

function showConfig() {
    document.getElementById('config-modal').classList.add('show');
}

function closeConfig() {
    document.getElementById('config-modal').classList.remove('show');
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
            alert('✅ Configuration sauvegardée !');
            closeConfig();
        } else {
            alert('Erreur lors de la sauvegarde');
        }
    } catch (error) {
        alert('Erreur: ' + error.message);
    }
}

// Close modals on outside click
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('show');
    }
}
